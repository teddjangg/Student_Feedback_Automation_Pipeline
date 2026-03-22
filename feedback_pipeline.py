import gspread
import pandas as pd
import numpy as np
from google.oauth2.service_account import Credentials
from google import genai
import time

def feedbackauto(spreadsheet_name, worksheet_name, api_key):


    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(
        "service_account.json",
        scopes=scope
    )

    client = gspread.authorize(creds)

    # name of spreadsheet
    spreadsheet = client.open(spreadsheet_name)
    worksheet = spreadsheet.worksheet(worksheet_name)

    values = worksheet.get_all_values()

    class_name = values[0][0]
    header = values[2]
    rows = values[4:]

    percent_idx = [
        i for i, col in enumerate(header)
        if col.strip().lower() == "percent"
    ]

    data = [
        [row[1]] +[row[5]]+[row[i] for i in percent_idx]
        for row in rows
    ]
    columns = ['Name'] + ['Avg'] + [f'hw{i+1}p' for i in range(len(percent_idx))]

    df = pd.DataFrame(data, columns=columns)

    # get number of HWs
    hw = [col for col in df.columns if col != 'Name' and col!= 'Avg']

    df[hw] = df[hw].replace({
        '': '제외',
        'N/A': '미제출'
    })

    df['Avg'] = df['Avg'].replace({
        '#DIV/0!' : '평균없음'
    })


    llm_client = genai.Client(api_key= api_key)


    reports = []

    total = len(df)

    for idx, (_, row) in enumerate(df.iterrows(), 1):
        print(f"[{idx}/{total}] {row['Name']} 처리 중...")
        hw_text = ""

        # produce HW score row
        for i, col in enumerate(hw, 1):
            hw_text += f"HW{i}: {row[col]}\n"
        
        # Process Average value (remove % then change to float)
        avg_raw = row['Avg']
        try:
            avg_score = float(str(avg_raw).replace('%', '').strip())
        except ValueError:
            avg_score = None
        
        # if Avg is bigger than 60, add a sentence (possible to get GPA A) 
        if avg_score is not None and avg_score >= 60:
            required_sentence = "보통 Quiz 평균이 60점 이상이면 GPA에서 A를 기대할 수 있습니다."
        else:
            required_sentence = ""
        
        # count HW not submitted 
        missing_count = sum(row[col] == '미제출' for col in hw)
        
        # not submitted more than half -> skip
        valid_hw = [col for col in hw if row[col] != '제외']
        submitted_count = sum(row[col] != '미제출' for col in valid_hw)

        if len(valid_hw) == 0:
            reports.append({
                "Name": row["Name"],
                "Report": "수업 참여 데이터가 없어 리포트를 생성할 수 없습니다."
            })
            continue

        if submitted_count < len(valid_hw) / 2:
            reports.append({
                "Name": row["Name"],
                "Report": "제출된 과제가 충분하지 않아 리포트 작성이 어렵습니다."
            })
            continue
            
            
        system_prompt = """
        당신은 학부모에게 보내는 학원 수업 피드백 문자를 작성하는 선생님입니다.
        항상 정중하고 자연스럽고 따듯한 어조로 작성하세요.
        """
        style_prompt = """
        반드시 아래 예시의 말투와 형식을 최대한 비슷하게 따라 작성하세요. 

        [예시]
        안녕하세요. 학원에서 AP Calculus를 가르치고 있는 선생입니다.
        OO의 성적은 평균 00점으로 매우 우수합니다.
        보통 Quiz 점수에서 평균 60점 이상이면 GPA에서 A를 기대할 수 있고, 남은 AP Calculus 실전반 과정까지 잘 마무리했을 때,
        실제 시험에서도 좋은 결과를 기대할 수 있는 실력이라고 보시면 됩니다.
        OO의 특정 Quiz 성적이 다른 Quiz 성적과 비교하면 조금 낮은 것 같더라도, 전체적으로 괜찮다면 크게 걱정하지 않으셔도 된다는 식으로 표현하세요.
        Quiz를 채점하는 것만으로 수업이 끝난 것이 아니라, 틀린 문제와 헷갈리는 문제들까지 수업 시간을 통해 확실히 이해하고 습득하도록 지도했다는 내용을 포함하세요.
        마지막은 앞으로의 기대를 담아 따뜻하게 마무리하세요.
        """
    
        rule_prompt = f"""
        [필수 포함 규칙]
        - 항상 정중하고 자연스럽게 작성
        - 부정적인 표현보다 긍정적인 표현 우선
        - 평균 점수 반드시 언급
        - 학생 이름과 수업 이름 자연스럽게 반영
        - 3~4문단의 완성된 문자 형식으로 작성

        [필수 포함 문장]
        -{required_sentence}
        """
        
        data_prompt = f"""
        [학생 정보]
        학생 이름: {row['Name']}
        수업 이름: {class_name}
        평균 점수: {row['Avg']}

        [Quiz 정보]
        {hw_text}
        """
        final_prompt = """
        이 학생에 대한 학부모용 피드백을 작성하세요.
        """
    
        prompt = f"""
        {system_prompt}
        
        {style_prompt}
        
        {rule_prompt} 
        
        {data_prompt}
        
        {final_prompt}
        """

        response = llm_client.models.generate_content(
            model = 'gemini-2.5-flash',
            contents = prompt
        )
        reports.append({
            "Name": row["Name"],
            "Report": response.text
        })
        
        time.sleep(2)

    result_df = pd.DataFrame(reports)
    filename = f"{worksheet_name}_student_reports.xlsx"
    result_df.to_excel(filename, index=False)
    print('Finished')

from pathlib import Path
import pandas as pd
import datetime
try:
    import pickle
except ImportError:
    import cloudpickle as pickle
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
import numpy as np


_THRESHOLD = .6
app_dir = Path(__file__).parent

#LOAD MODEL/SCALER
with open(app_dir / 'model.pkl', 'rb') as f:
    model = pickle.load(f)
with open(app_dir / 'fitted_scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)


#PROCESS df_main:
def get_df_main():

    df = pd.read_csv(app_dir / "rawraw.csv", dtype= {'average_monthly_hours': float, 'last_evaluation': float, 'time_spend_company': float, 'salary': int})

    def transform_row(row):
        return {
            'last_evaluation': row['last_evaluation'] / 10.0,
            'work_accident': 1 if row['work_accident'] else 0,
            'number_project': row['number_project'],
            'average_monthly_hours': row['average_monthly_hours'],
            'time_spend_company': row['time_spend_company'],
            'promotion_last_5years': 1 if row['promotion_last_5years'] else 0,
            'salary': 0 if row['salary_amount'] < 12000000 else 1 if row['salary_amount'] < 20000000 else 2
        }

    transformed_df = df.apply(transform_row, axis=1, result_type='expand')

    df['prob'] = model.predict_proba(scaler.transform(transformed_df))[:,1]
    df['prob'] = df.apply(lambda x: None if x['gone'] else x['prob'], axis=1)

    df['Leaving/Staying'] = df['prob'].apply(lambda x: 'Staying' if x < _THRESHOLD else 'Leaving')
    df['salary_group'] = transformed_df['salary'].astype(int)

    bins = [0, 5, 7, 10] 
    labels = ['Bad', 'Neutral', 'Good']

    df['satisfaction_group'] = pd.cut(df['satisfaction_level'], bins=bins, labels=labels, right=False)

    # dept_map = {
    #             'sales': 'Sales',
    #             'accounting': 'Accounting',
    #             'hr': 'Human Resources',
    #             'technical': 'Technical',
    #             'support': 'Support',
    #             'management': 'Management',
    #             'IT': 'IT',
    #             'product_mng': 'Product Manager',
    #             'marketing': 'Marketing',
    #             'RandD': 'R&D'
    #             }
    
    # left_map =  {
    #              1: 'Leaving',
    #              0: 'Staying'       
    #             }

    
    # df['department'] = df['department'].map(dept_map)
    # df['left'] = df['left'].map(left_map)
    return df

#LOAD CSVs
date_parser = lambda x: datetime.datetime.strptime(x, '%d/%m/%Y')
df_survey = pd.read_csv(app_dir / "survey.csv", parse_dates=['Date'], date_parser=date_parser)
df_in_out = pd.read_csv(app_dir / "in_out.csv", dtype=int)
df_main = get_df_main()
df_salaries = pd.read_csv(app_dir / "salaries.csv")

_DEPT_LIST = list(df_main['department'].unique())



def process_inputs(last_evaluation, number_project, average_monthly_hours, time_spend_company, work_accident, promotion_last_5years, salary):

    temp = pd.DataFrame([{
            'last_evaluation': last_evaluation/10.0,
            'work_accident': 1 if work_accident else 0,
            'number_project': number_project,
            'average_monthly_hours': average_monthly_hours,
            'time_spend_company': time_spend_company,
            'promotion_last_5years': 1 if promotion_last_5years else 0,
            'salary': 0 if salary < 12000000 else 1 if salary < 20000000 else 2
        }])

    return scaler.transform(temp)

def beau_column_names(which_one=True):
    rename_dict = {
            'id': 'Employee ID',
            'name': 'Employee Name',
            'time_spend_company': 'Years since Onboarding',
            'satisfaction_level': 'Satisfaction Score',
            'last_evaluation': 'Last Evaluation Score',
            'number_project': 'Total Projects Worked On',
            'work_accident': 'Logged Work Accident',
            'average_monthly_hours': 'Average Hours Worked (Monthly)',
            'promotion_last_5years': 'Promoted within last 5 years',
            'salary_amount': 'Salary',
            'prob': 'Probability of Leaving',
            'department': 'Department',
            'gone': 'Departed'
    }

    return df_main.rename(columns = rename_dict)


_COLS_TO_DROP = [
                # 'gone',
                'satisfaction_group',
                'Leaving/Staying',
                'salary_group'
                ]
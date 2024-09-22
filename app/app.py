from shiny import reactive
from shiny.express import input, render, ui
from shared import df_main, df_survey, model, process_inputs, beau_column_names, df_in_out
from shared import _THRESHOLD, _COLS_TO_DROP, _DEPT_LIST
from shinywidgets import render_plotly
import shinyswatch
import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import random
import pandas as pd


_SEL_ALL = 'SELECT ALL'
_PREV_SEL = False
_DARK_COLOR = '#000000'
_LIGHT_FONT = '#ffffff'
_HIGHLIGHT_COLOR = '#999999'
_PCT = random.uniform(25,85)

ui.page_opts(title="Employees Churn Rate",
            fillable=True,
            theme=shinyswatch.theme.cyborg
            )


#REACTIVE VALUE
temp_df_main = reactive.value(beau_column_names().drop(columns = _COLS_TO_DROP))
temp_df_survey = reactive.value(df_survey)

#SET DARK MODE PLOTS
custom_style = {
                'axes.labelcolor': _LIGHT_FONT,
                'xtick.color': _LIGHT_FONT,
                'ytick.color': _LIGHT_FONT,
                'text.color': _LIGHT_FONT,
                'axes.facecolor': _DARK_COLOR,
                'axes.edgecolor': _DARK_COLOR,
                'grid.color': _LIGHT_FONT,
                'figure.facecolor': _DARK_COLOR
               }
sns.set_style("darkgrid", rc=custom_style)

colors = [
    '#32CD32',  # Lime Green
    '#FF4500',  # Orange Red
    '#4682B4',  # Steel Blue
    '#FFD700',  # Gold
    '#FF6347',  # Tomato
    '#FF69B4',  # Hot Pink
    '#8A2BE2',  # Blue Violet
    '#00CED1',  # Dark Turquoise
    '#FF8C00',  # Dark Orange
    '#DC143C',  # Crimson
    '#20B2AA'   # Light Sea Green
]
sns.set_palette(colors)

ui.nav_spacer()


#KPI CARD FORMAT
def kpi(title, num):
    return ui.tags.div(
        ui.tags.div(
            ui.tags.p(f'{title}'),
            style = "font-size: 2rem;"
        ),
    ui.tags.p('{0:.2f}'.format(num)),
    style = f"font-size: 4rem; text-align: center; font-weight: bold; line-height:1; color: white;"
    )





##########################################################################################################################
#FIRST PAGE
##########################################################################################################################
with ui.nav_panel("Overview"):

    #PLOTS
    with ui.card(full_screen=True):
        with ui.navset_card_tab():
    
            with ui.nav_panel("Current Employees"):
                with ui.tooltip(id="toggle_tooltip",placement='top'):
                    ui.div(
                        ui.input_switch("stackswitch", "Toggle prediction", width='auto'),
                        style="margin-right: 0; margin-left:auto;"
                    )
                    "Click to toggle the breakdown of predicted outcome."

                @render.plot
                @reactive.event(input.stackswitch)
                def plot_1():
                    
                    temp = df_main[df_main['gone'] == 0][['department','satisfaction_level', 'Leaving/Staying']].groupby(['department', 'Leaving/Staying']).count().reset_index()

                    if input.stackswitch():
                        temp_stay = temp[temp['Leaving/Staying'] == 'Staying']
                        temp_leave = temp[temp['Leaving/Staying'] == 'Leaving']


                        ax = sns.barplot(x='department', y='satisfaction_level', data=temp_stay, color='green', label='Staying')
                        sns.barplot(x='department', y='satisfaction_level', data=temp_leave, color='red', label='Leaving', bottom=temp[temp['Leaving/Staying'] == 'Staying']['satisfaction_level'].values)

                        ax.bar_label(ax.containers[0], fmt='%d', label_type='center')


                    
                        for i, bar in enumerate(ax.containers[1]):  

                            adjusted_label = temp_leave.iloc[i]['satisfaction_level']
                            stay_value = temp_stay.iloc[i]['satisfaction_level']

                            ax.text(
                                bar.get_x() + bar.get_width() / 2, 
                                bar.get_height() + stay_value+20,  
                                f'{int(adjusted_label)}', ha='center', va='center'
                            )
                            
                        ax.set_title('Estimated total employees staying/leaving in each department')
                        plt.legend()
                    else:
                        ax = sns.barplot(temp, x='department', y='satisfaction_level',estimator='sum', errorbar=None, palette=colors)
                        ax.bar_label(ax.containers[0])
                        ax.set_title('Total employees in each department')

                    ax.set_xlabel("")
                    ax.set_ylabel("")

                    return ax
                
                ui.div(
                    ui.card_footer('*Prediction based on past 10 years employees data, and is flagged as "Leaving" when the calculated probability exceeds 40%. Salaries adjusted for inflation.'),
                    style="font-weight: bold; font-style: italic;background-color: black; color: white; margin-bottom:-15px; width: 100%; text-align: right;"
                )


            with ui.nav_panel("Satisfaction Score"):
                with ui.layout_columns(col_widths=(8,4,12)):
                    with ui.card(full_screen=True):
                        
                        @render.plot
                        def plot_osat():
                            temp = df_main[df_main['gone'] == 0][['department','satisfaction_level']]
                            
                            ax = sns.boxplot(data=temp, x='satisfaction_level',
                                                y = 'department',
                                                palette=colors,            
                                                whiskerprops=dict(color='white'),
                                                capprops=dict(color='white'),
                                                medianprops=dict(color='white'),
                                                flierprops=dict(markerfacecolor='white', markeredgecolor='white', marker='o')
                                            )
                            ax.set_xlabel('Satisfaction Score')
                            ax.set_ylabel('')

                            return ax


                    with ui.layout_columns(col_widths=(-1,12,-1)):
                        with ui.card(full_screen=True):

                            avg = df_main[df_main['gone'] == 0]['satisfaction_level'].mean()
                            target = 8
                            color = 'red' if avg < target else 'green'

                            ui.div(
                                ui.tags.p('Average Overall:'),
                                ui.div(
                                    ui.tags.p('{0:.2f}{1}'.format(avg, '👎' if target > avg else '👍')),
                                    style=f"color: {color}"
                                ),
                                ui.div(
                                    ui.tags.p('Target: {0:.1f}'.format(target)),
                                    style= " font-size: 1rem !important; text-align: right; padding-right: .2rem;"
                                ),
                                style = "text-align: center; background-color: black; font-size: 3rem; height: auto; margin-bottom: -2rem;"
                            )

                        with ui.card(full_screen=True):
                            ui.card_header(f"Total Response: {len(df_main[df_main['gone'] == 0])}")
                            @render.plot
                            def asd():
                                temp = df_main[df_main['gone'] == 0][['department','satisfaction_group']]

                                fig, ax = plt.subplots()

                                temp = temp['satisfaction_group'].value_counts()
                                custom_labels = ['Bad (1-5)', 'Neutral (5-7)', 'Good (7-10)']
                                colors = ['red', 'yellow', 'green']


                                wedges, texts, autotexts = ax.pie(temp, 
                                                                labels=custom_labels, 
                                                                autopct='%1.1f%%', 
                                                                startangle=90,
                                                                colors=colors,
                                                                textprops={'fontsize': 12, 'color': 'black'})
                                ax.legend(wedges, custom_labels, title=None, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
                                

                                ax.axis('equal')

                                return ax

            with ui.nav_panel("Incoming and Departing"):
                @render.plot
                def plot_churn():
                    
                    ax = df_in_out.plot(kind='bar', x='year')

                    ax.legend(['Incoming', 'Departing'])
                    ax.axvspan(-.5,2.5, facecolor=_HIGHLIGHT_COLOR, alpha=0.3)
                    ax.set_xlabel('')

                    for c in ax.containers:
                        ax.bar_label(c)

                    return ax

                ui.div(
                    ui.card_footer('*Company went public in 2017.'),
                    style="font-weight: bold; font-style: italic;background-color: black; color: white; margin-bottom:-15px; width: 100%; text-align: right;"
                )






##################################################################################################################################################################
#SECOND PAGE
##################################################################################################################################################################

with ui.nav_panel("Deep Dive"):
    with ui.card(full_screen=True):
            with ui.navset_card_tab():
                with ui.nav_panel(title='Calculate Probability!'):
                    with ui.layout_columns(col_widths=(4,8)):
                        with ui.card(full_screen=True):
                            with ui.layout_columns(col_widths=(6,6)):
                                ui.input_numeric('time_spend_company', 'Number of Years Working for Here', 1)
                                ui.input_numeric('number_project', "Total Projects (Ongoing/Completed)",1)
                                ui.input_numeric('average_monthly_hours', "Average Hours Worked per Month",160)
                                ui.input_select('promotion_last_5years', 'Promotion within the Last 5 Years', [False,True])
                                ui.input_numeric('last_evaluation', "Last Evaluation Score (1-10)",1, min=0, max=10)
                                ui.input_select('work_accident', "Logged Worked Accident", [False,True])
                                ui.input_numeric('salary', 'Current Salary', 12000000, min=8000000, step=1000000)
                                ui.tags.div(
                                    ui.input_action_button('predict', 'Predict!', width="100%"),
                                    style= "margin-top:2rem;"
                                )

                        with ui.card(full_screen=True):
                            with ui.card(full_screen=True, height="55%"):

                                result_text = reactive.value(
                                    ui.tags.div(
                                        '← Input correct details and press "Predict!" button',
                                    style = f"font-size: 7rem; text-align: center; font-weight: bold; line-height:1; color: white;"
                                    )
                                )

                                @render.ui
                                def render_result_text():
                                    return result_text()
                                
                                @reactive.effect
                                @reactive.event(input.predict)
                                def predict_result():

                                    result = model.predict_proba(process_inputs(
                                                                input.last_evaluation(),
                                                                input.number_project(),
                                                                input.average_monthly_hours(),
                                                                input.time_spend_company(),
                                                                input.work_accident(),
                                                                input.promotion_last_5years(),
                                                                input.salary()
                                                                ))

                                    no, yes = result[0]
                                    color = '#DC143C' if yes > _THRESHOLD else '#32CD32'
                                    num, word = (yes*100, 'leaving 😔')  if no < _THRESHOLD else (no*100, 'staying 😃')

                                    txt = ui.tags.div(
                                        ui.tags.div(
                                            ui.tags.p('{0:.2f}%'.format(num)),
                                            style = "font-size: 14rem; color: white;"
                                        ),
                                    ui.tags.p(f'of {word}'),
                                    style = f"font-size: 7rem; text-align: center; font-weight: bold; line-height:1; color: {color};"
                                    )

                                    result_text.set(txt)

                                ui.div(
                                    ui.card_footer('*prediction is for the event happening within 3 months from today'),
                                    style="font-weight: bold; font-style: italic;color: white; line-height: 0; text-align: right;"
                                )

                            with ui.card(full_screen=True, height="45%"):
                                ui.tags.div(
                                    ui.tags.h4('Happening most like due to (xxxxxxxxxx)'),
                                    ui.tags.h4('Current reported satisfaction score (xxxxxxxxxx)'),
                                    ui.tags.h4('Check on (xxxxxxxxxxxxxxx)'),
                                    ui.tags.h4('Reduce (xxxxxxxx) to (xxxxxxxxxxxxx)'),
                                    ui.tags.h4('Increase effort on (xxxxxxxxxxxxx)'),
                                )
                                
                ############################################
                #SURVEY RESULT PANEL
                ############################################
                with ui.nav_panel('Surveys'):
                    with ui.layout_columns(col_widths=(2,10)):

                        with ui.card(fillable=True):
                            ui.input_select('dept_3', 'Department', _DEPT_LIST)
                            ui.input_slider("pct_slider_2", "Chance to Leave (%)", min=0, max=100, value=(0, 100), step=1)
                            ui.input_date_range('dt_rng_2', 'Date Range', start=df_survey['Date'].min(), end=df_survey['Date'].max(), min=df_survey['Date'].min(), max=df_survey['Date'].max())

                            ui.input_action_button('filter_both', 'Apply Filter')

                            @reactive.effect
                            @reactive.event(input.filter_both)
                            def update_filters():
                                ui.update_select('dept_2', selected = input.dept_3())
                                ui.update_select('dept_1', selected = input.dept_3())
                                ui.update_date_range('dt_rng_1', start=input.dt_rng_2()[0], end=input.dt_rng_2()[1])
                                ui.update_slider('pct_slider_1', value=(input.pct_slider_2()[0], input.pct_slider_2()[1]))

                                #SURVEY SIDE
                                temp_df = df_survey.copy()

                                input_list = {
                                    'Department': input.dept_3()
                                }

                                filters = ' & '.join([f"(temp_df['{k}'].astype(str).str.contains('{v}', case=False))" for k, v in input_list.items() if pd.notna(v)])

                                temp_df = temp_df[eval(filters) & temp_df['Date'].between(pd.to_datetime(input.dt_rng_2()[0]) or df_survey['Date'].min(),pd.to_datetime(input.dt_rng_2()[1]) or df_survey['Date'].max())]

                                temp_df_survey.set(temp_df)

                                #MAIN SIDE
                                temp_df = beau_column_names()

                                input_list = {
                                            'Department': input.dept_3()
                                            }

                                filters = ' & '.join([f"(temp_df['{k}'].astype(str).str.contains('{v}', case=False))" for k,v in input_list.items() if pd.notna(v)])
                                filters+=f" & temp_df['Probability of Leaving'].between({input.pct_slider_2()[0]/200.0},{input.pct_slider_2()[1]/100.0})"

                                temp_df = temp_df[eval(filters)].drop(columns = _COLS_TO_DROP)

                                temp_df_main.set(temp_df)


                        
                        with ui.card(fillable=True, height='25%'):
                            ui.card_header('Average Score on Each Driver')
                            with ui.layout_columns(col_widths=(3,3,3,3)):
                                with ui.card(fillable=True):
                                    @render.ui
                                    def kpi1():
                                        return kpi('Work-Life Balance', temp_df_survey()['Work-Life Balance'].mean())                                

                                with ui.card(fillable=True):
                                    @render.ui
                                    def kpi2():
                                        return kpi('Workload', temp_df_survey()['Workload'].mean())

                                with ui.card(fillable=True):
                                    @render.ui
                                    def kpi3():
                                        return kpi('Management', temp_df_survey()['Management'].mean())
                                
                                with ui.card(fillable=True):
                                    @render.ui
                                    def kpi4():
                                        return kpi('Career Progression', temp_df_survey()['Growth Opportunities'].mean())

                            with ui.card(fillable=True, height='75%'):
                                with ui.layout_columns(col_widths=(4,8)):
                                    with ui.card(fillable=True):

                                        with ui.card(fillable=True):

                                            worst = reactive.value('IT')
                                            best = reactive.value('Support')

                                            @reactive.effect
                                            @reactive.event(input.filter_both)
                                            def randomise_best_worst():
                                                dl = _DEPT_LIST.copy()
                                                random.shuffle(dl)
                                                worst.set(dl.pop())
                                                best.set(dl.pop())

                                            with ui.card(fillable=True, height="50%"):
                                                @render.ui
                                                def kpi5():
                                                    return ui.tags.div(
                                                        ui.tags.div(
                                                            ui.tags.p('Worst Performer'),
                                                            style = "font-size: 2.5rem;"
                                                        ),
                                                    ui.tags.p(f'{worst()}'),
                                                    style = f"font-size: 3rem; text-align: center; font-weight: bold; line-height:1.3; color: white; overflow: hidden;"
                                                    )

                                            with ui.card(fillable=True, height="50%"):
                                                @render.ui
                                                def kpi6():
                                                    return ui.tags.div(
                                                        ui.tags.div(
                                                            ui.tags.p('Best Performer'),
                                                            style = "font-size: 2.5rem;"
                                                        ),
                                                    ui.tags.p(f'{best()}'),
                                                    style = f"font-size: 3em; text-align: center; font-weight: bold; line-height:1.3; color: white;, overflow: hidden;"
                                                    )

                                    with ui.card(fillable=True):
                                        @render.plot
                                        def kp():
                                            temp_df = temp_df_survey().copy()
                                            temp_df = temp_df[['Department', 'Work-Life Balance','Salary','Management','Workload','Growth Opportunities']].groupby('Department').mean().reset_index()

                                            ax = temp_df.plot(kind='bar', x='Department')
                                            ax.set_xlabel('')
                                            ax.set_xticklabels(list(temp_df['Department'].unique()),rotation=45, ha='right')
                                            return ax
#####################################################################################################################################################
#THIRD PAGE
#####################################################################################################################################################

with ui.nav_panel("Raw Data"):
    with ui.navset_card_tab():

        #EMPLOYEE DATA
        with ui.nav_panel("Employee Data"):
            with ui.layout_columns(col_widths=(2,10,12)):

                with ui.card(fillable=True):
                    with ui.card(fillable=True):
                        ui.input_text('name_1','Employee Name')
                        ui.input_numeric('id_1', 'Employee ID', None)
                        ui.input_select('dept_1', 'Department', _DEPT_LIST)
                        ui.input_slider("pct_slider_1", "Chance to Leave (%)", min=0, max=100, value=(0, 100), step=1, ticks=True)

                        ui.input_action_button('filter_main', 'Apply Filter')

                    with ui.card(fillable=True, max_height='4.5rem'): 
                        
                        @render.download(filename='employee_data.csv', label='export to csv')
                        def download_main():
    
                            yield temp_df_main().to_csv(index=False)
                        
                @reactive.effect
                @reactive.event(input.filter_main)
                def apply_filter_main():
                    temp_df = beau_column_names()

                    input_list = {
                                'Employee Name': input.name_1(),
                                'Employee ID': input.id_1(),
                                'Department': input.dept_1()
                                }

                    filters = ' & '.join([f"(temp_df['{k}'].astype(str).str.contains('{v}', case=False))" for k,v in input_list.items() if pd.notna(v)])
                    filters+=f" & temp_df['Probability of Leaving'].between({input.pct_slider_1()[0]/100.0},{input.pct_slider_1()[1]/100.0})"

                    temp_df = temp_df[eval(filters)].drop(columns = _COLS_TO_DROP)

                    temp_df_main.set(temp_df)



                with ui.card(fillable=True):
                    @render.table
                    def plot_df_main():
                        
                        return (
                            temp_df_main().head(100).style.set_table_attributes(
                                    'class="dataframe shiny-table table w-auto"'
                                )
                                .hide(axis="index")
                                .format(
                                    {
                                        "Satisfaction Score": "{0:0.2f}",
                                        "Years since Onboarding": "{0:0.2f}",
                                        "Last Evaluation Score": "{0:0.2f}",
                                        "Salary": "{0:,}",
                                        "Probability of Leaving": "{0:.2%}"

                                    }
                                )
                                .set_table_styles(
                                    [dict(selector="th", props=[("text-align", "left")])]
                                )
                            )
      
        ######################################
        # SURVEY TABLE
        ######################################
        with ui.nav_panel("Survey Data"):
            with ui.layout_columns(col_widths=(2, 10, 12)):
                with ui.card(fillable=True):
                    with ui.card(fillable=True):

                        ui.input_text('name_2', 'Employee Name')
                        ui.input_numeric('id_2', 'Employee ID', None)
                        ui.input_date_range('dt_rng_1', 'Date Range', start=df_survey['Date'].min(), end=df_survey['Date'].max(), min=df_survey['Date'].min(), max=df_survey['Date'].max())
                        ui.input_select('dept_2', 'Department', _DEPT_LIST)
                        ui.input_action_button('filter_survey', 'Apply Filter')

                    with ui.card(fillable=True, max_height='4.5rem'):
                        @render.download(filename='survey_data.csv', label='export to csv')
                        def download_survey():
                            yield temp_df_survey().to_csv(index=False)


                @reactive.effect
                @reactive.event(input.filter_survey)
                def apply_filter_survey():
                    temp_df = df_survey.copy()

                    input_list = {
                        'Employee Name': input.name_2(),
                        'Employee ID': input.id_2(),
                        'Department': input.dept_2()
                    }

                    filters = ' & '.join([f"(temp_df['{k}'].astype(str).str.contains('{v}', case=False))" for k, v in input_list.items() if pd.notna(v)])
                    


                    temp_df = temp_df[eval(filters) & temp_df['Date'].between(pd.to_datetime(input.dt_rng_1()[0]) or df_survey['Date'].min(),pd.to_datetime(input.dt_rng_1()[1]) or df_survey['Date'].max())]

                    temp_df_survey.set(temp_df)

                with ui.card(fillable=True):
                    @render.table
                    def plot_df_survey():
                        return temp_df_survey().head(100)

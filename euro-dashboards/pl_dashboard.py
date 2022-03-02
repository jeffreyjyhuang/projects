import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import requests
import json
from pandas import json_normalize
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots

# Color Palette: #E63946, #F4F4F0, #A8DADC, #457B9D, #1D3557

@st.cache(allow_output_mutation=True, ttl = 24*60*60)
def teams_data(season, league):

    # Getting Standings Data
    standings_url = "https://api-football-v1.p.rapidapi.com/v3/standings"
    standings_querystring = {"season":season,"league":league}
    standings_headers = {
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
        'x-rapidapi-key': "074d08d02amsh7dd6783945864b1p1340dajsnf3b3318593b0"
        }

    standings_response = requests.request("GET", standings_url, headers=standings_headers, params=standings_querystring)
    standings_response = json.loads(standings_response.text)['response']
    standings = json_normalize(standings_response)
    standings = pd.DataFrame(standings['league.standings'][0][0])
    standings = pd.concat([standings.drop(['team'], axis=1), standings['team'].apply(pd.Series)], axis=1)
    
    # Function that inputs a team and outputs
    def team_stats(team_id):
        team_url = "https://api-football-v1.p.rapidapi.com/v3/teams/statistics"
        team_querystring = {"league": league ,"season":season,"team":team_id}
        team_headers = {
            'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
            'x-rapidapi-key': "074d08d02amsh7dd6783945864b1p1340dajsnf3b3318593b0"
            }

        response = requests.request("GET", team_url, headers=team_headers, params=team_querystring)
        response = json.loads(response.text)['response']
        return json_normalize(response)

    # Combining standings data with team data
    standings['more_stats'] = standings.apply(lambda x: team_stats(x['id']), axis=1)

    return standings


# Running Streamlit App
def main():
    # CONFIGURATIONS
    st.set_page_config(layout="wide")

    pio.templates.default = "simple_white"
    px.defaults.template = "ggplot2"
    px.defaults.color_continuous_scale = px.colors.sequential.Blackbody
    px.defaults.width = 900
    px.defaults.height = 400
    

    # IMPORT DATA (Change this if league changes)
    # All Leagues
    all_leagues = dict()
    for i in ['39', '135', '140', '61', '78']:
        all_leagues[i] = teams_data('2021', i)
    all_leagues = pd.concat(all_leagues)
    mid, middle_col, mid = st.beta_columns([20,60,20])
    with middle_col:
        st.title("European Soccer Leagues")
        st.markdown("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Turpis massa tincidunt dui ut ornare. Eros donec ac odio tempor orci. Imperdiet proin fermentum leo vel orci porta non pulvinar. In est ante in nibh mauris cursus. Auctor elit sed vulputate mi sit amet. Nunc consequat interdum varius sit amet mattis vulputate. Mi in nulla posuere sollicitudin aliquam. Neque gravida in fermentum et sollicitudin ac. Orci eu lobortis elementum nibh tellus. Vitae sapien pellentesque habitant morbi tristique senectus. Justo donec enim diam vulputate ut pharetra sit amet. Habitant morbi tristique senectus et netus et malesuada. Pellentesque diam volutpat commodo sed. Amet risus nullam eget felis eget nunc lobortis mattis.")
        # STANDINGS
        st.header("Standings")
        selected_league = st.selectbox("Select league(s)", options = 
                all_leagues['group'].value_counts()
                .index.to_list())
        league_data = all_leagues[all_leagues['group'] == selected_league]
        
        # TEAM STATS
        ## Extracting team data (separate dataframe within the 'more_stats' column)
        ## Need to add team data to have a more comprehensive standings table
        league_data['team_name'] = league_data['name']
        league_data = league_data.set_index('name') # for easier querying
        team_data = pd.concat(list(league_data['more_stats']))
        team_data['team_name'] = team_data['team.name']
        team_data.set_index('team.name', inplace = True)
        
        ## Outputing standings (but with team stats now )
        team_data['GoalsDiff'] = team_data['goals.for.total.total'] - team_data['goals.against.total.total']
        standings_final = team_data[['team_name',
                                    'fixtures.played.total',
                                    'fixtures.wins.total',
                                    'fixtures.draws.total',
                                    'fixtures.loses.total',
                                    'goals.for.total.total',
                                    'goals.against.total.total',
                                    'GoalsDiff',
                                    'form']]\
                        .rename(columns = {'team_name':'Team Name',
                                            'fixtures.wins.total': 'W',
                                            'fixtures.draws.total': 'D',
                                            'fixtures.loses.total': 'L',
                                            'fixtures.played.total': 'MP',
                                            'goals.for.total.total': 'GF',
                                            'goals.against.total.total': 'GA',
                                            'GoalsDiff':'GD',
                                            'form': 'Form'})

        ## Empty row inserted so that the index matches the actual rank of the standings table
        empty_row = pd.DataFrame([[np.nan] * len(standings_final.columns)], columns=standings_final.columns)
        standings_final = empty_row.append(standings_final, ignore_index = True)
        st.table(standings_final.iloc[1:,:])


        # GFGA STATS
        st.header("Defensive and Offensive Metrics")
        st.markdown("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Turpis massa tincidunt dui ut ornare. Eros donec ac odio tempor orci. Imperdiet proin fermentum leo vel orci porta non pulvinar. In est ante in nibh mauris cursus. Auctor elit sed vulputate mi sit amet. Nunc consequat interdum varius sit amet mattis vulputate. Mi in nulla posuere sollicitudin aliquam. Neque gravida in fermentum et sollicitudin ac. Orci eu lobortis elementum nibh tellus. Vitae sapien pellentesque habitant morbi tristique senectus. Justo donec enim diam vulputate ut pharetra sit amet. Habitant morbi tristique senectus et netus et malesuada. Pellentesque diam volutpat commodo sed. Amet risus nullam eget felis eget nunc lobortis mattis.")
        GFGA_scatter = px.scatter(team_data,
                    x = team_data['goals.for.average.total'].apply(float),
                    y = team_data['goals.against.average.total'].apply(float),
                    text = 'team_name',
                    title = "Average Goals For vs Average Goals Against",
                    color_discrete_sequence=['#457B9D'])
        GFGA_scatter.update_xaxes(range = [0, 3.0],
                                    title_text = 'Average Goals Scored Per Game',
                                    titlefont_size = 13,
                                    tickfont_size = 13,
                                    showgrid=True,)\
                    .update_yaxes(range = [0,2.5],
                                    title_text = 'Average Goals Conceded Per Game',
                                    titlefont_size = 13,
                                    tickfont_size = 13,
                                    showgrid=True,)\
                    .update_traces(textposition = 'top center')\
                    .update_layout(height = 1200, width = 1200,
                                    font_family="verdana",
                                    font_color="black",
                                    plot_bgcolor = '#F4F4F0')
                
        st.plotly_chart(GFGA_scatter)
        st.header("More League Statistics")
        st.markdown("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Turpis massa tincidunt dui ut ornare. Eros donec ac odio tempor orci. Imperdiet proin fermentum leo vel orci porta non pulvinar. In est ante in nibh mauris cursus. Auctor elit sed vulputate mi sit amet. Nunc consequat interdum varius sit amet mattis vulputate. Mi in nulla posuere sollicitudin aliquam. Neque gravida in fermentum et sollicitudin ac. Orci eu lobortis elementum nibh tellus. Vitae sapien pellentesque habitant morbi tristique senectus. Justo donec enim diam vulputate ut pharetra sit amet. Habitant morbi tristique senectus et netus et malesuada. Pellentesque diam volutpat commodo sed. Amet risus nullam eget felis eget nunc lobortis mattis.")
    ## Columns
    mid,col1, col2, col3,mid= st.beta_columns([8,25,25,25,8])
    with col1:
        cleansheet_bardata = team_data[['team_name','clean_sheet.home', 'clean_sheet.away', 'clean_sheet.total']]\
                            .melt(id_vars = ['team_name'], value_vars = ['clean_sheet.home', 'clean_sheet.away'])\
                            .rename(columns = {'team_name': 'Name', 'variable': 'cs_type', 'value': 'count'})\
                            .sort_values('count', ascending = True)
        cleansheet_bardata['cs_type'] = np.where(cleansheet_bardata['cs_type'] == 'clean_sheet.home', 'home', 'away')
        cleansheet_bar = px.bar(cleansheet_bardata,
                            y='Name',
                            x='count',
                            color = 'cs_type',
                            title = "Number of Clean Sheets",
                            color_discrete_map = {
                                "home": "#A8DADC",
                                "away": "#E63946"},
                            category_orders={"cs_type": ["home", "away"]})
        cleansheet_bar.update_xaxes(title_text = 'Average Goals Scored Per Game',
                            titlefont_size = 13,
                            tickfont_size = 13,
                            showgrid=True,)\
            .update_yaxes(title_text = 'Team',
                            titlefont_size = 13,
                            tickfont_size = 13,
                            showgrid=True,)\
            .update_layout(height = 800, width = 600,
                            font_family="verdana",
                            font_color="black",
                            legend=dict(orientation="h", y = 1.05, 
                            x = -0.1, title = None),
                            plot_bgcolor = '#F4F4F0')
        st.plotly_chart(cleansheet_bar)

    with col2:
        FTS_bardata = team_data[['team_name', 'failed_to_score.away', 'failed_to_score.home']]\
                        .melt(id_vars = ['team_name'], value_vars = ['failed_to_score.away', 'failed_to_score.home'])\
                        .rename(columns = {'team_name': 'Name', 'variable': 'FTS_type', 'value': 'count'})\
                        .sort_values('count', ascending = True)
        FTS_bardata['FTS_type'] = np.where(FTS_bardata['FTS_type'] == 'failed_to_score.home', 'home', 'away')
        FTS_bar = px.bar(FTS_bardata,
                            y='Name',
                            x='count',
                            color = 'FTS_type',
                            title = "Number of Missed Opportunities",
                            color_discrete_map = {
                                "home": "#A8DADC",
                                "away": "#E63946"},
                            category_orders={"FTS_type": ["home", "away"]})
        FTS_bar.update_xaxes(title_text = 'Missed Opportunities',
                            titlefont_size = 13,
                            tickfont_size = 13,
                            showgrid=True,)\
            .update_yaxes(title_text = '',
                            titlefont_size = 13,
                            tickfont_size = 13,
                            showgrid=True,)\
            .update_layout(height = 800, width = 600,
                            font_family="verdana",
                            font_color="black",
                            legend=dict(orientation="h", y = 1.05, 
                            x = -0.1, title = None),
                            plot_bgcolor = '#F4F4F0')
        st.plotly_chart(FTS_bar)
    with col3:
        penalty_bardata = team_data[['team_name','penalty.scored.total', 'penalty.missed.total']]\
                            .melt(id_vars = ['team_name'], value_vars = ['penalty.scored.total', 'penalty.missed.total'])\
                            .rename(columns = {'team_name': 'Name', 'variable': 'penalty_type', 'value': 'count'})\
                            .sort_values('count', ascending = True)
        penalty_bardata['penalty_type'] = np.where(penalty_bardata['penalty_type'] == 'penalty.scored.total', 'scored', 'missed')
        penalty_bar = px.bar(penalty_bardata,
                            y='Name',
                            x='count',
                            color = 'penalty_type',
                            title = "Penalties Missed/Scored",
                            color_discrete_map = {
                                "scored": "#A8DADC",
                                "missed": "#E63946"},
                            category_orders={"penalty_type": ["scored", "missed"]})
        penalty_bar.update_xaxes(title_text = 'Number of Penalties',
                            titlefont_size = 13,
                            tickfont_size = 13,
                            showgrid=True,)\
            .update_yaxes(title_text = '',
                            titlefont_size = 13,
                            tickfont_size = 13,
                            showgrid=True,)\
            .update_layout(height = 800, width = 600,
                            font_family="verdana",
                            font_color="black",
                            legend=dict(orientation="h", y = 1.05, 
                            x = -0.1, title = None),
                            plot_bgcolor = '#F4F4F0')
        st.plotly_chart(penalty_bar)


    mid, middle, mid = st.beta_columns([20,60,20])
    with middle: 
        st.header("Team Data")
        st.markdown("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Turpis massa tincidunt dui ut ornare. Eros donec ac odio tempor orci. Imperdiet proin fermentum leo vel orci porta non pulvinar. In est ante in nibh mauris cursus. Auctor elit sed vulputate mi sit amet. Nunc consequat interdum varius sit amet mattis vulputate. Mi in nulla posuere sollicitudin aliquam. Neque gravida in fermentum et sollicitudin ac. Orci eu lobortis elementum nibh tellus. Vitae sapien pellentesque habitant morbi tristique senectus. Justo donec enim diam vulputate ut pharetra sit amet. Habitant morbi tristique senectus et netus et malesuada. Pellentesque diam volutpat commodo sed. Amet risus nullam eget felis eget nunc lobortis mattis.")
        # TEAM SELECTION & LOGO
        team_select_options = list(league_data.index.sort_values(ascending = True))
        ## Columns
        selected_team = st.selectbox('Select a team',\
            options = team_select_options, index = 0)
        misc_data = team_data[[
            "biggest.streak.loses",
            "biggest.streak.wins",
            "biggest.streak.draws",
            "biggest.loses.home",
            "biggest.loses.away",
            "biggest.wins.home",
            "biggest.wins.away"]]\
                .rename(columns = {
            "biggest.streak.loses" : "Biggest Losing Streak",
            "biggest.streak.wins": "Biggest Winning Streak",
            "biggest.streak.draws": "Biggest Drawing Streak",
            "biggest.loses.home": "Biggest Lost at home",
            "biggest.loses.away": "Biggest Lost Away",
            "biggest.wins.home": "Biggest Win at Home",
            "biggest.wins.away": "Biggest Win Away"
                }).T
    mid, coltable, mid = st.beta_columns([40,20,40])
    with coltable:
        st.table(misc_data[selected_team])
    mid, middle, mid = st.beta_columns([20,60,20])
    with middle:
        # GF/GD GROUPED BAR PLOT
        ## Preparing dataframe for plotting (wide format)
        columns_to_keep_gfgd = ['goals.for.minute.0-15.total',
                        'goals.for.minute.16-30.total',
                        'goals.for.minute.31-45.total',
                        'goals.for.minute.46-60.total',
                        'goals.for.minute.61-75.total',
                        'goals.for.minute.76-90.total',
                        'goals.against.minute.0-15.total',
                        'goals.against.minute.16-30.total',
                        'goals.against.minute.31-45.total',
                        'goals.against.minute.46-60.total',
                        'goals.against.minute.61-75.total',
                        'goals.against.minute.76-90.total']
                        
        gdbarplot_data = team_data.loc[selected_team][columns_to_keep_gfgd].reset_index()
        gdbarplot_data['type'] = np.where(gdbarplot_data['index'].str.contains('for') == True, 'For', 'Against')
        gdbarplot_data.rename(columns={selected_team: "goals",'index': 'minutes'}, inplace = True)
        gdbarplot_data['minutes'] = gdbarplot_data['minutes'].str.replace('.', '')
        gdbarplot_data['minutes'] = gdbarplot_data['minutes'].str.replace(r'[a-z]', '')
        gdbarplot_data['goals'] = np.where(gdbarplot_data['type'] == 'Against', -1 * gdbarplot_data['goals'], gdbarplot_data['goals'])

        GF_GD_bar = px.bar(gdbarplot_data,
                                y='goals',
                                x='minutes',
                                title = "Distribution of Goals Scored (For and Against)",
                                color = 'type',
                                color_discrete_map = {
                                "For": "#A8DADC",
                                "Against": "#E63946"},
                            category_orders={"type": ["For", "Against"]})
        GF_GD_bar.update_xaxes(title_text = 'Period in Game (Minutes)',
                            titlefont_size = 13,
                            tickfont_size = 13,
                            showgrid=True,)\
            .update_yaxes(title_text = 'Goal Count',
                            titlefont_size = 13,
                            tickfont_size = 13,
                            showgrid=True,)\
            .update_layout(height = 500, width = 800,
                            font_family="verdana",
                            font_color="black",
                            legend=dict(orientation="h", y = 1.1, 
                            x = 0.75 , title = None),
                            plot_bgcolor = '#F4F4F0')


        # CARDS GROUPED BAR PLOT
        columns_to_keep_cards = ['cards.yellow.0-15.total',
                        'cards.yellow.16-30.total',
                        'cards.yellow.31-45.total',
                        'cards.yellow.46-60.total',
                        'cards.yellow.61-75.total',
                        'cards.yellow.76-90.total',
                        'cards.red.0-15.total',
                        'cards.red.16-30.total',
                        'cards.red.31-45.total',
                        'cards.red.46-60.total',
                        'cards.red.61-75.total',
                        'cards.red.76-90.total']
        cards_barplot = team_data.loc[selected_team][columns_to_keep_cards].reset_index()
        cards_barplot['type'] = np.where(cards_barplot['index'].str.contains('yellow') == True, 'Yellow', 'Red')
        cards_barplot.rename(columns={selected_team: "cards",'index': 'minutes'}, inplace = True)
        cards_barplot['minutes'] = cards_barplot['minutes'].str.replace('.', '')
        cards_barplot['minutes'] = cards_barplot['minutes'].str.replace(r'[a-z]', '')
        cards_bar = px.bar(cards_barplot,
                                y='cards',
                                x='minutes',
                                title = "Distribution of Cards Received",
                                color = 'type',
                                color_discrete_map = {
                                "Yellow": "#A8DADC",
                                "Red": "#E63946"},
                            category_orders={"type": ["Yellow", "Red"]})
        cards_bar.update_xaxes(title_text = 'Period in Game (Minutes)',
                            titlefont_size = 13,
                            tickfont_size = 13,
                            showgrid=True,)\
            .update_yaxes(title_text = 'Card Count',
                            titlefont_size = 13,
                            tickfont_size = 13,
                            showgrid=True,)\
            .update_layout(height = 500, width = 800,
                            font_family="verdana",
                            font_color="black",
                            legend=dict(orientation="h", y = 1.1, 
                            x = 0.75 , title = None),
                            plot_bgcolor = '#F4F4F0')
    mid, col1, col2, mid = st.beta_columns([10,30,30,10])

    with col1:
        st.plotly_chart(cards_bar)
    with col2:
        st.plotly_chart(GF_GD_bar)

if __name__ == "__main__":
    main()

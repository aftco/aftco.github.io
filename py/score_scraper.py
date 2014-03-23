from datetime import datetime, timedelta
import urllib2
import json

#
#    configured teams to generate boxscores for
#
TEAMS = {
            #'lions': {'name': 'Lions', 'url': 'http://espn.go.com/nfl/team/_/name/det/detroit-lions'},
            'tigers': {'name': 'Tigers', 'url': 'http://espn.go.com/mlb/team/_/name/det/detroit-tigers'},
            #'pistons': {'name': 'Pistons', 'url': 'http://espn.go.com/nba/team/_/name/det/detroit-pistons'},
            'red_wings': {'name': 'Red Wings', 'url': 'http://espn.go.com/nhl/team/_/name/det/detroit-red-wings'},
            'michigan_basketball': {'name': 'UofM Basketball', 'url': 'http://espn.go.com/mens-college-basketball/team/_/id/130/michigan-wolverines'},
            #'michigan_football': {'name': 'UofM Football', 'url': 'http://espn.go.com/college-football/team/_/id/130/michigan-wolverines'},
            'msu_basketball': {'name': 'MSU Basketball', 'url': 'http://espn.go.com/mens-college-basketball/team/_/id/127/michigan-state-spartans'},
            #'msu_football': {'name': 'MSU Football', 'url': 'http://espn.go.com/college-football/team/_/id/127/michigan-state-spartans'},
}

#
#    return BeautifulSoup html parser object
#
def get_html(url):
    from BeautifulSoup import BeautifulSoup

    html = urllib2.urlopen(url).read()
    return BeautifulSoup(html)


def main():
    for team in TEAMS:
        html = get_html(TEAMS[team]['url'])

        yesterday = datetime.now() - timedelta(days=1)
        last_game_recap = html.find("div", {"class": "mod-container mod-no-footer mod-game current"})

        #
        #   determine if game happened yesterday
        #
        if last_game_recap(text=datetime.strftime(yesterday, '%b %d')) != 0:
            details = {'team': team, 'date': datetime.strftime(yesterday, '%Y%m%d'), }
            venue = last_game_recap.find("div", {"class": "venue"})
            if venue:
                details['venue'] = venue.text
            else:
                details['venue'] = ''

            time = last_game_recap.find("div", {"class": "time"})
            if time:
                details['time'] = time.text
            else:
                details['time'] = ''

            scoring = last_game_recap.find("div", {"class": "scoring"})
            loser = scoring.find('table').findAll('tr')[1]
            winner = scoring.find('table').findAll('tr')[2]

            if TEAMS[team]['url'] in str(winner):
                our_scores = winner
                their_scores = loser
            else:
                our_scores = loser
                their_scores = winner

            scores = []
            scoring = last_game_recap.find("div", {"class": "scoring"})
            for td in our_scores.findAll('td'):
                text = td.text
                if text != '':
                    scores.append([text])

            count = 0
            for td in their_scores.findAll('td'):
                text = td.text
                if text != '':
                    scores[count].append(text)
                    count += 1
            details['scores'] = scores
            
            #
            #   parse scores
            #
            away_team = last_game_recap.find("div", {"class": "team team-away"})
            home_team = last_game_recap.find("div", {"class": "team team-home"})
            if TEAMS[team]['url'] == home_team("a")[0].attrs[0][1]:
                details['home'] = True
                details['opponent'] = away_team("h6")[0].text
            else:
                details['home'] = False
                details['opponent'] = home_team("h6")[0].text
            for link in last_game_recap.find("p", {"class": "links"}).findAll('a'):
                 if 'Box' in str(link):
                     details['link'] = 'http://espn.go.com%s' % link.attrs[0][1]
                     
            details['game_text'] = '%s @ %s' % (away_team("h6")[0].text, home_team("h6")[0].text)

        #
        #   print details as clean json
        #
        print json.dumps(details)
    

if __name__ == "__main__":
    main()    
    

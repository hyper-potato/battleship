from battleship_game import BattleshipGame
import csv
import os
import subprocess
import itertools
import signal


class TimeoutError(Exception):
    pass


def _handle_timeout(signum, frame):
    raise TimeoutError()


class BattleshipTournament(object):
    GAMES_PER_MATCH = 10
    
    def gen_commit_log(self):
        output = []
        
        for team in self.get_teams():
            rep = self.__teams_dict[team]
            wd = self.__get_dir(rep)
            
            if os.path.exists(wd):
                p = subprocess.run(['git',
                                    'log',
                                    '--date=iso',
                                    '--pretty=format:%h,%an,%ad,"%s"',
                                    'player.py'],
                                   stdout=subprocess.PIPE,
                                   cwd=wd)
                
                log = p.stdout.decode('utf-8').strip()
                
                for line in log.split('\n'):
                    output.append([team, rep] + line.split(',', 3))
                    
        with open('commit_log.csv', 'w') as f:
            csv.writer(f).writerows(output)

    def commit_repository(self, team_name):
        rep = self.__teams_dict[team_name]
        wd = self.__get_dir(rep)

        if os.path.exists(wd):
            print('[{0}] git add results_log.csv'.format(team_name))
            subprocess.run(['git', 'add', 'results_log.csv'],
                           stdout=subprocess.PIPE,
                           cwd=wd)

            print('[{0}] git commit'.format(team_name))
            subprocess.run(['git', 'commit', '-m', 'Tournament {0} results.'.format(self.__id)],
                           stdout=subprocess.PIPE,
                           cwd=wd)

            print('[{0}] git pull --rebase'.format(team_name))
            subprocess.run(['git', 'pull', '--rebase'],
                           stdout=subprocess.PIPE,
                           cwd=wd)

            print('[{0}] git push'.format(team_name))
            subprocess.run(['git', 'push', 'origin', 'master'],
                           stdout=subprocess.PIPE,
                           cwd=wd)

    # Given a repository, slice out the X.500. This becomes the directory
    # where the team's player.py file resides.
    def __get_dir(self, rep):
        return 'repositories' + rep[22:32]

    def __load_player(self, team_name):
        directory = self.__get_dir(self.__teams_dict[team_name])
        file = directory + 'player.py'

        print('Loading player.py for {0}'.format(team_name))
        locals_dict = {}
        with open(file) as f:
            code = compile(f.read(), file, 'exec')
            exec(code, locals_dict, locals_dict)

        p = locals_dict['Player'](team_name)
        return p

    # Loads a dictionary of teams and repositories from the registration
    # file. 
    def __load_teams(self, filename):
        d = {}
        with open(filename, 'r') as f:
            c = csv.reader(f)

            # Skips the header row
            next(c)

            for line in c:
                d[line[2]] = line[3]

        return d

    # Refreshes a team's repository with the latest version of their files.
    def pull_repository(self, team_name):
        rep = self.__teams_dict[team_name]
        wd = self.__get_dir(rep)

        if os.path.exists(wd):
            subprocess.run(['git', 'pull'], cwd=wd, stdout=subprocess.PIPE)
        else:
            subprocess.run(['git', 'clone', rep, wd], stdout=subprocess.PIPE)

        # reset player's log file for this tournament
        if os.path.exists(wd):
            file = wd + 'results_log.csv'
            open(file, 'w').close()

    # Writes information to a the results_log.csv file in the team's
    # repository.
    def __writelog(self, team_name, log_lines):
        directory = self.__get_dir(self.__teams_dict[team_name])
        file = directory + 'results_log.csv'

        if os.path.exists(directory):
            with open(file, 'a') as f:
                csv.writer(f).writerows(log_lines)

    # Writes a summary row to the main results.csv file, used to generate
    # the leaderboard.
    def __writesummary(self, log_line):
        with open('results.csv', 'a') as f:
            csv.writer(f).writerows(log_line)

    def get_teams(self):
        return self.__teams_dict

    # Runs a single game and logs the result.
    def run_game(self, team1, team2):
        p_list = []

        for t in [team1, team2]:
            # setup infinite loop handling
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(2)

            # Try to load each team's player.py file. If it doesn't exist,
            # log an error to that team's repository results.
            try:
                p_list.append(self.__load_player(t))
            except TimeoutError as e:
                log = [[-1,
                        'player_load',
                        t,
                        '',
                        'error',
                        'infinite loop detected']]       
            except Exception as e:
                log = [[-1,
                        'player_load',
                        t,
                        '',
                        'error',
                        str(e)]]
                self.__writelog(t, log)
            finally:
                signal.alarm(0)

        # If we have both players, then let the game begin!
        if len(p_list) == 2:
            self.__current_game += 1
            g = BattleshipGame(self.__current_game, p_list[0], p_list[1])
            log = g.run()

            for t in [team1, team2]:
                self.__writelog(t, log)

        self.__writesummary([log[-1]])

    # A match is a series of games between two players. The number of games
    # is controlled by the GAMES_PER_MATCH constant.
    def run_match(self, team1, team2):
        t1 = team1
        t2 = team2

        try:
            for i in range(self.GAMES_PER_MATCH):
                self.run_game(t1, t2)
                t1, t2 = t2, t1
        except FileNotFoundError as e:
            print(e)

    # Runs the tournament, pitting all players against each other. Pass
    # refresh=False to skip the repository refresh step (for performance).
    def run(self, refresh=True, commit=False):
        # Refresh all repositories
        if refresh:
            for t in self.__teams_dict:
                self.pull_repository(t)

        # itertools library generates all combinations of 2 teams and runs
        # GAMES_PER_MATCH games for each combination.
        for t1, t2 in itertools.combinations(self.__teams_dict, 2):
            self.run_match(t1, t2)

        if commit:
            for t in self.__teams_dict:
                self.commit_repository(t)

    def __init__(self, t_id, teams_file='teams.csv'):
        self.__teams_dict = self.__load_teams(teams_file)
        self.__id = t_id

        # ids are a 2-digit tournament id + a 5-digit game id
        # (total = 7 digits)
        self.__current_game = t_id * 100000

import signal


class TimeoutError(Exception):
    pass


def _handle_timeout(signum, frame):
    raise TimeoutError()


class BattleshipGame():
    def __init__(self, game_id, p1, p2):
        self.__game_id = game_id
        self.__p1 = p1
        self.__p2 = p2
        self.__log = []

    # returns the Player object that fails validation, or None if both
    # players pass the validation routine
    def __validate_boards(self, b1, b2):
        failed = None
        comment = '{0} returned an invalid game board: {1}'
        # Validate each player's board. If a player fails validation, the
        # other player wins by default
        # Players will alternate positions (p1 vs p2)
        # to ensure fairness
        valid = False
        try:
            valid = b1.validate()
            msg = comment.format(self.__p1.get_name(), str(b1))
        except Exception as e:
            msg = comment.format(self.__p1.get_name(), str(e))
        
        if not valid:
            self.__log.append([self.__game_id,
                               'board_validation',
                               self.__p1.get_name(),
                               '',
                               'error',
                               msg])
            self.__log.append([self.__game_id,
                               'game',
                               self.__p2.get_name(),
                               '',
                               'win',
                               self.__p1.get_name()])
            failed = self.__p1
        
        valid = False
        try:
            valid = b2.validate()
            msg = comment.format(self.__p2.get_name(), str(b2))
        except Exception as e:
            msg = comment.format(self.__p2.get_name(), str(e))
        
        if not valid:
            self.__log.append([self.__game_id,
                               'board_validation',
                               self.__p2.get_name(),
                               '',
                               'error',
                               msg])
            self.__log.append([self.__game_id,
                               'game',
                               self.__p1.get_name(),
                               '',
                               'win',
                               self.__p2.get_name()])
            failed = self.__p2

        return failed

    def get_log(self):
        return self.__log

    def run_rounds(self, b1, b2):
        game_over = False
        turn = 1

        while not game_over:
            if turn % 2 == 1:
                off_player = self.__p1
                def_player = self.__p2
                def_board = b2
            else:
                off_player = self.__p2
                def_player = self.__p1
                def_board = b1

            # We default to a miss
            result_tuple = (None, False, False)
            result_id = 'miss'
            cmt = ''
            shot_pos = ''
            
            # setup infinite loop handling
            # you might need to comment this out on Windows
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(2)

            try:
                shot_pos = off_player.next_shot()
                result_msg = '[{0}] {1} shoots at {2} and...'.format(turn,
                                                                     off_player.get_name(),
                                                                     shot_pos)
                shot_result = def_board.shoot_at(shot_pos)

                if shot_result:
                    cmt = shot_result.get_name()
                    if shot_result.is_sunk():
                        result_tuple = (shot_pos, True, True)
                        result_id = 'sink'
                        result_msg += 'sinks {0}\'s {1}!'.format(def_player.get_name(),
                                                                 shot_result.get_name())
                    else:
                        result_tuple = (shot_pos, True, False)
                        result_id = 'hit'
                        result_msg += 'hits {0}\'s {1}!'.format(def_player.get_name(),
                                                                shot_result.get_name())
                else:
                    result_tuple = (shot_pos, False, False)
                    result_msg += 'misses.'

                # Not everyone is implementing post_shot_result. Wrap in a
                # try block to prevent an error.
                try:
                    off_player.post_shot_result(result_tuple)
                except:
                    pass

            except TimeoutError as e:
                # Offensive player loses if they timeout
                result_id = 'error'
                winner_name = def_player.get_name()
                defeated_name = off_player.get_name()
                cmt = 'next_shot: did not return in 2 seconds'
                game_over = True
            except Exception as e:
                # Offensive player loses if they throw an exception
                result_id = 'error'
                winner_name = def_player.get_name()
                defeated_name = off_player.get_name()
                cmt = str(e)
                game_over = True
            finally:
                signal.alarm(0)
                
            self.__log.append([self.__game_id,
                           'shot',
                           off_player.get_name(),
                           str(shot_pos),
                           result_id,
                           cmt])

            if not game_over and not def_board.is_alive():
                print('[{0}] *** {1} wins ***'.format(turn, off_player.get_name()))
                winner_name = off_player.get_name()
                defeated_name = def_player.get_name()
                game_over = True
            else:
                turn += 1

        self.__log.append([self.__game_id,
                           'game',
                           winner_name,
                           '',
                           'win',
                           defeated_name])

        return off_player

    def run(self):
        valid = True
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(2)
        
        try:
            b1 = self.__p1.get_board()
        except Exception as e:
            valid = False
            self.__log.append([self.__game_id,
                   'get_board',
                   self.__p1.get_name(),
                   '',
                   'error',
                   'did not return a valid board within 2 seconds'])
            self.__log.append([self.__game_id,
                   'game',
                   self.__p2.get_name(),
                   '',
                   'win',
                   self.__p1.get_name()])
        finally:
            signal.alarm(0)

        signal.alarm(2)    
        try:
            b2 = self.__p2.get_board()
        except Exception as e:
            valid = False
            self.__log.append([self.__game_id,
                   'get_board',
                   self.__p2.get_name(),
                   '',
                   'error',
                   'did not return a valid board within 2 seconds'])
            self.__log.append([self.__game_id,
                   'game',
                   self.__p1.get_name(),
                   '',
                   'win',
                   self.__p2.get_name()])
        finally:
            signal.alarm(0)
    
        if valid:
            validation_result = self.__validate_boards(b1, b2)
    
            if not validation_result:
                self.run_rounds(b1, b2)

        return self.__log

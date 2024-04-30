from mindrove.board_shim import BoardShim, MindRoveInputParams, BoardIds
from pylsl import StreamInfo, StreamOutlet, local_clock

import logging

def send_lsl(board_shim):
    data = board_shim.get_board_data(100)
    outlet = StreamOutlet()

def main():
    #init of the board
    try:
        params = MindRoveInputParams()
        board_shim = BoardShim(BoardIds.MINDROVE_WIFI_BOARD, params)
        board_shim.prepare_session()
        board_shim.start_stream()

        send_lsl(board_shim)
    except BaseException:
        logging.warning('Exception', exc_info=True)
    finally:
        logging.info('End')
        if board_shim.is_prepared():
            logging.info('Releasing session')
            board_shim.release_session()


if __name__ == "__main__":
    main()

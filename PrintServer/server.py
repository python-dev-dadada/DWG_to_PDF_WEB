#
# SendPlot Server
#

import os
import subprocess
import signal
import sys
import logging
import configparser
from os import listdir, remove
from time import sleep, localtime, strftime

from os.path import join, dirname
from dotenv import load_dotenv

def initialize():
  # Read configuration file
  dotenv_path = join(dirname(__file__), '../.env')
  load_dotenv(dotenv_path)
  QUEUES          = os.environ.get('PRINT_QUEUE_ROOT')
  # FILES           = os.environ.get('PRINT_FILES_ROOT')
  LOG_FILE        = os.environ.get('PRINT_LOG_FILE')
  IVIEW           = os.environ.get('I_VIEW32')
  SCAN_INTERVAL   = float(os.environ.get('PRINT_SCAN_DELAY'))

  # Initialize logging
  logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s %(message)s')

  logging.info('========================= SendPlot Server startup =========================')
  logging.info('>>>>> Begin Initializing <<<<<')

  def signal_handler(signal, frame):
      print ('Shutting down SendPlot Server!')
      logging.info('\tshutting down...')
      logging.info('========================= SendPlot Server shutdown ========================')
      sys.exit(0)
  signal.signal(signal.SIGINT, signal_handler)
  logging.info('\t\t\t ===[ Press Ctrl+C to shutdown SendPlot Server ]===')

  # Display console startup message
  print ('========================= SendPlot Server startup =========================')
  print ('\t\t\t ===[ Press Ctrl+C to shutdown SendPlot Server ]===')
  print ('Monitoring...')

  # Scan for queues
  queue_count = 0
  plot_queues = {}
  logging.info('\tqueues\t' + QUEUES)
  while 1:
    if os.path.exists(QUEUES):
      for queue in listdir(QUEUES):
        if not queue.endswith('md'):
          queue_count += 1
          q_config                              = configparser.RawConfigParser()
          q_config.read(QUEUES + '\\' + queue + '\\i_view32.ini')
          print_config                          = q_config._sections['Print']
          q_struc                               = {'printer': print_config['printer'], 'path': QUEUES + '\\' + queue}
          plot_queues[queue]                    = q_struc

          logging.info('\t\t' + queue)
      break
    else:
      logging.warning('Cannot access queues:\t' + QUEUES)
      logging.warning('Waiting 60 seconds')
      sleep(60)

  logging.info('\t\t[' + str(queue_count) + '] queues scanned')

  # file_count = 0 
  # logging.info('\tfiles\t' + FILES)
  # for file in listdir(FILES):
  #   if not file.endswith('md'):
  #     file_count += 1
  # logging.info('\t\t[' + str(file_count) + '] files scanned')
  # logging.info('\tScan interval: ' + str(SCAN_INTERVAL) + ' seconds')
  logging.info('>>>>> Finished Initializing <<<<<')

  # Return initialized values
  return QUEUES, LOG_FILE, SCAN_INTERVAL, plot_queues, IVIEW

###############################################################################
if __name__ == "__main__":
  # Execute
  QUEUES, LOG_FILE, SCAN_INTERVAL, plot_queues, IVIEW = initialize()

  logging.info('Start monitoring queues...') 
  while 1: 
    # logging.info('\t' + 'monitoring...') 
    for queue in plot_queues:
      if os.path.exists(QUEUES + '\\' + queue):
        for file in listdir(QUEUES + '\\' + queue):
          if file.endswith('pdf') or file.endswith('PDF'):
            logging.info('\tprocessing\t' + queue.ljust(25) + '\t' + file)
            # logging.info(plot_queues[queue]['path'])
            queue_path = QUEUES + '\\' + queue
            cmd = IVIEW + ' ' + queue_path + '\\' + \
                  file + ' /ini="' + queue_path + \
                  '\\" /print="' + plot_queues[queue]['printer'] + '"'
            subprocess.call(cmd)
            # logging.info(cmd)
            # sleep(1)
            remove(QUEUES + '\\' + queue + '\\' + file)
      else:
        logging.warning('Cannot access queue:\t ' + QUEUES + '\\' + queue)
        logging.warning('Refreshing configuration in 60 seconds')
        sleep(60)
        QUEUES, LOG_FILE, SCAN_INTERVAL, plot_queues, IVIEW = initialize()       

    sleep(SCAN_INTERVAL)


import argparse
import logging.config
import yaml
import pickle
import pandas as pd


# Logging
logging_config = 'config/logging/local.conf'
logging.config.fileConfig(logging_config, disable_existing_loggers=False)
logger = logging.getLogger('run-reproducibility')

# logging.basicConfig(format='%(name)-12s %(levelname)-8s %(message)s', level=logging.DEBUG)


# import module/function from src foolder
from src.acquire import acquire
from src.clean import clean
from src.featurize import featurize
from src.train import train


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Train predictive model to classify clouds into one of two types based on cloud.data")

    parser.add_argument('step', help='Which step to run', choices=['acquire','clean','featurize','train'])
    parser.add_argument('--input', '-i', default=None, help='Path to input object')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--output', '-o', default=None, help='Path to save output object (optional, default = None)')
    parser.add_argument('--output1', '-o1', default=None, help='Path to save output object1 (optional, default = None)')

    args = parser.parse_args()

    # Load configuration file for parameters and tmo path
    with open(args.config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    logger.info("Configuration file loaded from %s" % args.config)
    
    # read input csv file as pandas dataframe
    if args.input is not None:
        input = pd.read_csv(args.input, low_memory=False)   
        logger.info('Input data loaded from %s', args.input)

    if args.step == 'acquire':
        output = acquire(**config['acquire'])
    elif args.step == 'featurize':
        output = featurize(input, **config['featurize'])
    elif args.step == 'clean':
        output = clean(input, **config['clean'])
    elif args.step == 'train':
        output, output1 = train(input, **config['train'])
    else:
        logger.warning('No such argument as %s', args.step)

    if args.output is not None:
        # if train, output model pkl file, else output csv file
        if args.step == 'train':
            try:
                pickle.dump(output,open(args.output,'wb'))             
            except:
                logger.error("Model object can't be dumped!")

            output1.to_csv(args.output1, index=False)
            logger.info("Output saved to %s" % args.output1)

        else:
            output.to_csv(args.output, index=False)
        
        logger.info("Output saved to %s" % args.output)
        

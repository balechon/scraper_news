import argparse
import logging
logging.basicConfig(level=logging.INFO)
import pandas as pd
from urllib.parse import urlparse
import re
import hashlib
import nltk
from nltk.corpus import stopwords
import datetime
# nltk.download('punkt')
# nltk.download('stopwords')

stop_words=set(stopwords.words('spanish'))

def run(filename):
    logging.info('Starting cleanign process')
    df=_read_data(filename)
    newpaper_uid=_extract_newspaper_uid(filename)
    df=_add_newspaper_uid(df, newpaper_uid)
    df=_extract_host(df)
    df=_clean_text(df,'title')
    df=_clean_text(df,'body')
    df=_add_uid(df)
    df=_add_token(df,'title')
    df=_add_token(df,'body')

    df=_drop_duplicates(df,'title')
    df=_drop_rows_with_mising_data(df)
    _save_data(df,filename)

    return df

def _save_data(df,filename):
    name='clean_{}'.format(filename)
    df.to_csv(name)


def _drop_rows_with_mising_data(df):
    logging.info('drop rows with missing data')
    return df.dropna()

def _drop_duplicates(df,name):
    logging.info('removing the duplicates values {} column'.format(name))
    df.drop_duplicates(subset=name, keep='first',inplace=True)
    return df


def _add_token(df,column_name):
    name_column='tokens_{}'.format(column_name)
    df[name_column]=(
                    df[column_name].apply(lambda row: nltk.word_tokenize(row))
                    .apply(lambda tokens: list(filter(lambda token: token.isalpha(),tokens)))
                    .apply(lambda tokens: list(map(lambda token: token.lower(),tokens)))
                    .apply(lambda word_list: list(filter(lambda word: word not in stop_words,word_list)))
                    .apply(lambda valid_word_list: len(valid_word_list))
                    )
    return df

def _add_uid(df):
    logging.info('Adding a unique encoding url')
    uids= (df['link'].apply(lambda url: hashlib.md5(url.encode()))
            .apply(lambda has: has.hexdigest()))
    df['uid']=uids
    df.set_index('uid',inplace=True)
    return df


def _clean_text(df,column):
    logging.info('Cleanig the {} column'.format(column))
    df[column]=df[column].str.replace(re.compile(r"\',|\'|\\n|\[|\]|\\xa+\d"),'')
    return df
def _extract_host(df):
    logging.info('Extracting host from links')
    df['host']=df['link'].apply(lambda url: urlparse(url).netloc)
    return df

def _add_newspaper_uid(df,newpaper_uid):
    logging.info('Adding news Paper Uid column with {}'.format(newpaper_uid))
    df['newspaper_uid']=newpaper_uid
    return df

def _extract_newspaper_uid(filename):
    logging.info('Extracting uid. .')
    news_paper_uid= filename.split('_')[0]
    return news_paper_uid

def _read_data(filename):
    logging.info('Reading the file {}'.format(filename))
    return pd.read_csv(filename)


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filename',
        help='The path to the dirty data',
        type=str
    )
    args= parser.parse_args()

    df=run (args.filename)
    print(df)
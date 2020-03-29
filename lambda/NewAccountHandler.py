import csv
import boto3
import os
import re
import logging
import cfnresource
from urllib.request import urlopen


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def validateinput(row):
    validation = True
    errormsg = " "
    emailexpression = '[^\s@]+@[^\s@]+\.[^\s@]+'
    # Check all the required fields are specified
    accountname = row['AccountName']
    accountemail = row['AccountEmail']
    ssouseremail = row['SSOUserEmail']
    orgunit = row['OrgUnit']
    ssouserfirstname = row['SSOUserFirstName']
    ssouserlastname = row['SSOUserLastName']

    if accountname == 'None':
        validation = False
        errormsg = errormsg + "AccountName is a required field., "
    if accountemail == 'None':
        validation = False
        errormsg = errormsg + "AccountEmail is a required field., "
    if ssouseremail == 'None':
        validation = False
        errormsg = errormsg + "SSOUserEmail is a required field., "
    if orgunit == 'None':
        validation = False
        errormsg = errormsg + "OrgUnit is a required field., "
    if ssouserfirstname == 'None':
        validation = False
        errormsg = errormsg + "SSOUserFirstName is a required field., "
    if ssouserlastname == 'None':
        validation = False
        errormsg = errormsg + "SSOUserLastName is a required field., "
    if len(accountname) > 50:
        validation = False
        errormsg = errormsg + "AccountName can't be more than 50 characters., "
    if len(accountemail) < 7:
        validation = False
        errormsg = errormsg + "AccountEmail has to be more than 6 characters., "
    if len(ssouseremail) < 7:
        validation = False
        errormsg = errormsg + "SSOUserEmail has to be more than 6 characters., "
    if re.match(emailexpression, accountemail) is None:
        validation = False
        errormsg = errormsg + "AccountEmail is not valid., "
    if re.match(emailexpression, ssouseremail) is None:
        validation = False
        errormsg = errormsg + "SSOUserEmail is not valid., "
    LOGGER.info('Validation status {} and error message {} '.format(validation, errormsg))
    return (str(validation), errormsg)


def account_handler(event, context):
    try:
        table_name = os.environ.get("TABLE_NAME")
        acct_creation_input_url = os.environ.get("BATCH_ACCT_INPUT")
        dyno = boto3.client("dynamodb")
        file = urlopen(acct_creation_input_url)
        fcontent = file.read().decode('utf-8')
        for row in csv.DictReader(fcontent.splitlines()):
            (validation, errormsg) = validateinput(row)
            response = dyno.put_item(
                Item={
                    'AccountName': {
                        'S': row['AccountName'],
                    },
                    'SSOUserEmail': {
                        'S': row['SSOUserEmail'],
                    },
                    'AccountEmail': {
                        'S': row['AccountEmail'],
                    },
                    'SSOUserFirstName': {
                        'S': row['SSOUserFirstName'],
                    },
                    'SSOUserLastName': {
                        'S': row['SSOUserLastName'],
                    },
                    'OrgUnit': {
                        'S': row['OrgUnit'],
                    },
                    'Valid': {
                        'S': validation
                    },
                    'Processed': {
                        'S': 'N'
                    },
                    'ErrroMsg': {
                        'S': errormsg
                    }
                },
                TableName=table_name,
            )
        #Send success message back to cloudformation
        responseData = {}
        cfnresource.send(event,context,cfnresource.SUCCESS,responseData,"CustomResourcePhysicalID")
    except Exception as e:
        LOGGER.error(e)

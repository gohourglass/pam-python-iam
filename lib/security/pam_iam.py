import boto, cookielib, os, urllib, urllib2, sys, syslog

AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""

iam = boto.connect_iam(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

# Sorta cheating here
ORG_NAME = iam.get_account_alias()['list_account_aliases_response']['list_account_aliases_result']['account_aliases'][0]

class NoRedirection(urllib2.HTTPErrorProcessor):
  def http_response(self, request, response):
    return response

  https_response = http_response

def authorize(username):
  return username in [x['user_name'] for x in iam.get_all_users()['list_users_response']['list_users_result']['users']]

def authenticate(username, password):
  cj = cookielib.CookieJar()
  opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor(cj))

  data = "redirect_uri=https%%3A%%2F%%2Fconsole.aws.amazon.com%%2Fconsole%%2Fhome%%3Fstate%%3DhashArgs%%2523%%26isauthcode%%3Dtrue&forceMobileApp=&forceMobileLayout=&isIAMUser=1&mfaLoginFailure=&Action=login&RemainingExpiryPeriod=&account=%(account)s&username=%(username)s&password=%(password)s&mfacode=&next_mfacode=&client_id=arn:aws:iam::015428540659:user/homepage"
  data = data % {
    'username': username,
    'password': password,
    'account': ORG_NAME
  }

  req = urllib2.Request('https://signin.aws.amazon.com/oauth', headers={"Referer":"https://signin.aws.amazon.com"}, data=data)
  resp = opener.open(req)
  return resp.code == 302

def auth_log(msg):
  syslog.openlog(facility=syslog.LOG_AUTH)
  syslog.syslog("pam_python.so %s" % msg)
  syslog.closelog()

def pam_sm_authenticate(pamh, flags, argv):
  try:
    user = pamh.get_user(None)
  except pamh.exception, e:
    return e.pam_result
  if not user:
    return pamh.PAM_USER_UNKNOWN

  authorized = authorize(user)
  if not authorized:
    return pamh.PAM_USER_UNKNOWN
 
  try:
    resp = pamh.conversation(pamh.Message(pamh.PAM_PROMPT_ECHO_OFF, "%s's Password:"%user))
  except pamh.exception, e:
    return e.pam_result

  authenticated = authenticate(user, resp.resp)
  if authenticated:
    return pamh.PAM_SUCCESS

  return pamh.PAM_AUTH_ERR 

def pam_sm_setcred(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_acct_mgmt(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_open_session(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_close_session(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_chauthtok(pamh, flags, argv):
  return pamh.PAM_SUCCESS

if __name__ == '__main__':
  import sys
  print authorize(sys.argv[1])

pam-python-crowd
================

This is a mechanism for logging into a Linux computer using Amazon's IAM service.

Currently, if the user doesn't have a matching account in /etc/passwd, one will be created via potentially unsafe use of `pam_exec.so`.

NOTE: If the user doesn't yet exist locally, it will be created -- however, it will fail to auth until a second try at login. This is due to PAM not noticing when a user is created mid-authorization.

Requirements
------------

* pam_python (I used the version from the ubuntu repositories)
* pam_exec (to run the script to add the user when they login the first time).
* An AWS account with IAM properly set up.

1. Copy `usr/share/pam-configs/pam_config_python_iam` into `/usr/share/pam-configs`
1. Ensure your IAM is set up properly (Sign-in url, user with login profile, etc)
1. Edit lib/security/pam_iam.py to set the AWS credentials. I recommend using a specific set of IAM creds for this
1. Copy lib/security/pam_iam.py to /lib/security
1. Install the python modules `boto` and `pyquery`.
1. Copy `usr/local/bin/mk-iam-user` to `/usr/local/bin`
1. Run `pam-auth-update` and enable "PAM_Python Module with pam_iam.py".  Save the config.
1. Try logging in using an IAM user's credentials


# lambda-assetmatcher
An AWS-lambda-digiroad API to unify the properties of the Finnish national digital road network data with multiple slightly differing and redundant data sources from municipalities' own databases.

## Current "CI"
Compress the files into a zip file, and upload to aws lambda :)

## Accessing PostgreSQL:
Generate rsa keypair, and send the public key to Sampsa

Tutorial: https://help.github.com/en/enterprise/2.15/user/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

SSH to RDS proxy-machine (admin@54.194.25.104) using the key pair (accept the unknown host public key fingerprint).

Change user to postgres with <code>sudo su postgres</code>

Connect to RDS with <code>psql -h digiroad.ciav7xehyayg.eu-west-1.rds.amazonaws.com -d dr_r</code>


## Example usage:

URL:https://b25ldra733.execute-api.eu-west-1.amazonaws.com/dev/convert<br/>
Method: POST<br/>
##### Headers:<br/>
Content-type:application/json <br/>
Body: test.json

Response: List of matched digiroad road link ids

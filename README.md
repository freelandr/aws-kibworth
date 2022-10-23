# Serverless functions and API for Kibworth Ancestry project

## Usage

### Deployment

```
$ serverless deploy
```


### Invocation

```bash
export PASSWD=[insert password here]
curl -i -H 'Content-Type: application/json' -X POST -d '{"password": "$PASSWD"}' https://dov9dia7k5.execute-api.us-east-1.amazonaws.com/stop_rds
curl -i -H 'Content-Type: application/json' -X POST -d '{"password": "$PASSWD"}' https://dov9dia7k5.execute-api.us-east-1.amazonaws.com/restore_rds
```

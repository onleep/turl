from Dotenv import env
from redis import ConnectionPool, Redis

pool = ConnectionPool(host=env.get('REDIS_IP'),
                      password=env.get('REDIS_PASS'),
                      port=6379,
                      decode_responses=True)
redis = Redis(connection_pool=pool)

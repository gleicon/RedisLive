from api.util import settings
import sqliteprovider
import redisprovider
import txredisprovider


# TODO: Confirm there's not some implementation detail I've missed, then
# ditch the classes here.
class RedisLiveDataProvider(object):

    @staticmethod
    def get_provider(data_store_type = None):
        """Returns a data provider based on the settings file.

        Valid providers are currently Blocking/Tornado Redis, txRedisAPI based for twitsted and cyclone and SQLite.
        """
        if (data_store_type == None): 
            data_store_type = settings.get_data_store_type()

        # FIXME: Should use a global variable for "redis" here.
        if data_store_type == "redis":
            return redisprovider.RedisStatsProvider()
        elif data_store_type == "txredis":
            return txredisprovider.TxRedisStatsProvider()
        else:
            return sqliteprovider.RedisStatsProvider()

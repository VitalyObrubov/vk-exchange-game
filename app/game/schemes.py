from marshmallow import Schema, fields


class Security(Schema):
    id = fields.Str()
    description = fields.Str()
    price = fields.Int()
    market_event = fields.Str()


class BuyedSecurity(Schema):
    security = fields.Nested(Security, many=False, required=True)
    ammount = fields.Int(required=True)


class User(Schema):
    vk_id = fields.Int(required=False)
    name = fields.Str(required=True)
    create_at = fields.Date(required=True)
    points = fields.Int(required=False)
    buyed_securites = fields.Dict(keys=fields.Str(),values=fields.Nested(BuyedSecurity))
    state = fields.Str(required=True)


class Game(Schema):
    id = fields.Int(required=False)
    create_at = fields.Date(required=True)
    chat_id = fields.Int(required=False)
    state = fields.Str(required=True)
    trade_round = fields.Int(required=False)
    users = fields.Dict(keys=fields.Int(),values=fields.Nested(User))
    traded_sequrites = fields.Dict(keys=fields.Str(),values=fields.Nested(Security))
    

class ListGameSchema(Schema):
    game = fields.Dict(keys=fields.Str(),values=fields.Nested(Game))


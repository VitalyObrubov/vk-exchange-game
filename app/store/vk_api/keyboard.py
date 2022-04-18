START_KEY = {
  "one_time": True,
  "buttons": [
    [
      {
        "action": {
          "type": "callback",
          "label": "Старт",
          "payload": {"command":"/start_game"}
        },
        "color": "negative"
      },
      {
        "action": {
          "type": "callback",
          "label": "Помощь",
          "payload": {"command":"/help"}
        },
        "color": "primary"
      }
    ]
  ]
}

RUN_KEY = {
  "one_time": True,
  "buttons": [
     [
      {
        "action": {
          "type": "callback",
          "label": "Купить",
          "payload": {'command':'/buy'}
        },
        "color": "positive"
      },
      {
        "action": {
          "type": "callback",
          "label": "Продать",
          "payload": {'command':'/sell'}
        },
        "color": "primary"
      }
    ],
   [
      {
        "action": {
          "type": "callback",
          "label": "Инфо",
          "payload": {'command':'/info'}
        },
        "color": "positive"
      },
      {
        "action": {
          "type": "callback",
          "label": "Помощь",
          "payload": {'command':'/help'}
        },
        "color": "primary"
      }
    ],
    [
      {
        "action": {
          "type": "callback",
          "label": "Закончить раунд",
          "payload": {'command':'/finish'}
        },
        "color": "secondary"
      },
      {
        "action": {
          "type": "callback",
          "label": "Закончить игру",
          "payload": {'command':'/stop_game'}
        },
        "color": "negative"
      }
    ]
  ]
}


def kbd_sell(d_securs):
  securs = list(d_securs.values())
  res = {
    "inline": True,
    "buttons": [
      [
        {
          "action": {
            "type": "callback",
            "label": f"{securs[0].id}-{securs[0].price}",
            "payload": {'command':'/sell','secur':securs[0].id}
          },
          "color": "positive"
        },
        {
          "action": {
            "type": "callback",
            "label": f"{securs[1].id}-{securs[1].price}",
            "payload": {'command':'/sell','secur':securs[1].id}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": f"{securs[2].id}-{securs[2].price}",
            "payload": {'command':'/sell','secur':securs[2].id}
          },
          "color": "positive"
        }
      ],
      [
        {
          "action": {
            "type": "callback",
            "label": f"{securs[3].id}-{securs[3].price}",
            "payload": {'command':'/sell','secur':securs[3].id}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": f"{securs[4].id}-{securs[4].price}",
            "payload": {'command':'/sell','secur':securs[4].id}
          },
          "color": "secondary"
        },
        {
          "action": {
            "type": "callback",
            "label": f"{securs[5].id}-{securs[5].price}",
            "payload": {'command':'/sell','secur':securs[5].id}
          },
          "color": "negative"
        }
      ]
    ]
  }
  return res

def kbd_sell_ammount(secur_id):
  res = {
    "inline": True,
    "buttons": [
      [
        {
          "action": {
            "type": "callback",
            "label": "1",
            "payload": {'command':'/sell','secur':secur_id,'ammount':'1'}
          },
          "color": "positive"
        },
        {
          "action": {
            "type": "callback",
            "label": "2",
            "payload": {'command':'/sell','secur':secur_id,'ammount':'2'}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": "3",
            "payload": {'command':'/sell','secur':secur_id,'ammount':'3'}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": "4",
            "payload": {'command':'/sell','secur':secur_id,'ammount':'4'}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": "5",
            "payload": {'command':'/sell','secur':secur_id,'ammount':'5'}
          },
          "color": "positive"
        }
      ],
      [
        {
          "action": {
            "type": "callback",
            "label": "6",
            "payload": {'command':'/sell','secur':secur_id,'ammount':'6'}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": "7",
            "payload": {'command':'/sell','secur':secur_id,'ammount':'7'}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": "8",
            "payload": {'command':'/sell','secur':secur_id,'ammount':'8'}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": "9",
            "payload": {'command':'/sell','secur':secur_id,'ammount':'9'}
          },
          "color": "secondary"
        },
        {
          "action": {
            "type": "callback",
            "label": "10",
            "payload": {'command':'/sell','secur':secur_id,'ammount':'10'}
          },
          "color": "negative"
        }
      ]
    ]
  }
  return res

def kbd_buy(d_securs):
  securs = list(d_securs.values())
  res = {
    "inline": True,
    "buttons": [
      [
        {
          "action": {
            "type": "callback",
            "label": f"{securs[0].id}-{securs[0].price}",
            "payload": {'command':'/buy','secur':securs[0].id}
          },
          "color": "positive"
        },
        {
          "action": {
            "type": "callback",
            "label": f"{securs[1].id}-{securs[1].price}",
            "payload": {'command':'/buy','secur':securs[1].id}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": f"{securs[2].id}-{securs[2].price}",
            "payload": {'command':'/buy','secur':securs[2].id}
          },
          "color": "positive"
        }
      ],
      [
        {
          "action": {
            "type": "callback",
            "label": f"{securs[3].id}-{securs[3].price}",
            "payload": {'command':'/buy','secur':securs[3].id}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": f"{securs[4].id}-{securs[4].price}",
            "payload": {'command':'/buy','secur':securs[4].id}
          },
          "color": "secondary"
        },
        {
          "action": {
            "type": "callback",
            "label": f"{securs[5].id}-{securs[5].price}",
            "payload": {'command':'/buy','secur':securs[5].id}
          },
          "color": "negative"
        }
      ]
    ]
  }
  return res

def kbd_buy_ammount(secur_id):
  res = {
    "inline": True,
    "buttons": [
      [
        {
          "action": {
            "type": "callback",
            "label": "1",
            "payload": {'command':'/buy','secur':secur_id,'ammount':'1'}
          },
          "color": "positive"
        },
        {
          "action": {
            "type": "callback",
            "label": "2",
            "payload": {'command':'/buy','secur':secur_id,'ammount':'2'}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": "3",
            "payload": {'command':'/buy','secur':secur_id,'ammount':'3'}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": "4",
            "payload": {'command':'/buy','secur':secur_id,'ammount':'4'}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": "5",
            "payload": {'command':'/buy','secur':secur_id,'ammount':'5'}
          },
          "color": "positive"
        }
      ],
      [
        {
          "action": {
            "type": "callback",
            "label": "6",
            "payload": {'command':'/buy','secur':secur_id,'ammount':'6'}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": "7",
            "payload": {'command':'/buy','secur':secur_id,'ammount':'7'}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": "8",
            "payload": {'command':'/buy','secur':secur_id,'ammount':'8'}
          },
          "color": "primary"
        },
        {
          "action": {
            "type": "callback",
            "label": "9",
            "payload": {'command':'/buy','secur':secur_id,'ammount':'9'}
          },
          "color": "secondary"
        },
        {
          "action": {
            "type": "callback",
            "label": "10",
            "payload": {'command':'/buy','secur':secur_id,'ammount':'10'}
          },
          "color": "negative"
        }
      ]
    ]
  }
  return res  
import json
START_KEY = {
  "one_time": True,
  "buttons": [
    [
      {
        "action": {
          "type": "text",
          "label": "Старт",
          "payload": {"command":"/start_game"}
        },
        "color": "negative"
      },
      {
        "action": {
          "type": "text",
          "label": "Помошь",
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
          "type": "text",
          "label": "Инфо",
          "payload": "{\"command\":\"/info\"}"
        },
        "color": "positive"
      },
      {
        "action": {
          "type": "text",
          "label": "Помошь",
          "payload": "{\"command\":\"/help\"}"
        },
        "color": "primary"
      }
    ],
    [
      {
        "action": {
          "type": "text",
          "label": "Закончить раунд",
          "payload": "{\"command\":\"/finish\"}"
        },
        "color": "secondary"
      },
      {
        "action": {
          "type": "text",
          "label": "Закончить игру",
          "payload": "{\"command\":\"/stop_game\"}"
        },
        "color": "negative"
      }
    ]
  ]
}


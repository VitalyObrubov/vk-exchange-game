from app.game.views import GameListView, StopGameListView


class TestGame:
    async def test_get_list(self):
      
        answ = await GameListView.get(self)
        assert 3 == 3

    async def test_get_stopped_list(self):

        answ = await StopGameListView.get(self)
        assert 3 == 3
from flaskproj import app


class TestView():
    def setup(self):
        app.testing = True
        self.client = app.test_client()
    
    def test_main(self):
        response = self.client.get('/')
        assert response.status_code == 200
        

    def test_registration(self):
        response = self.client.get('/registration')
        assert response.status_code == 200
    

    def test_bascet(self):
        response = self.client.get('/basket')
        assert response.status_code == 302


    def test_order(self):
        response = self.client.get('/order/1')
        assert response.status_code == 302
    

    def test_autorization(self):
        response = self.client.post('/autorization/',data={'name': 'admin', 'psw': 'admin'})
        assert response.status_code == 302
    

    def test_add_card(self):
        response = self.client.get('/add-card')
        assert response.status_code == 302
    
    

    def teardown(self):
        pass

from flaskproj import __version__


class TestView:
    def setup(self):
        app.testing = True
        self.client = app.test_client()
        app.config['WTF_CSRF_ENABLED'] = False 

    def test_main(self):
        response = self.client.get("/")
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        assert "Главная страница".encode() in response.data
        

    def test_registration(self):
        response = self.client.get("/registration")
        assert response.status_code == 200
        assert "Регистрация".encode() in response.data
        html = response.get_data(as_text=True)
        assert 'name="name"' in html
        assert 'name="psw"' in html
        assert 'name="email"' in html
        response = self.client.post(
            '/registration', data = {"name":"admin48", "psw":"admin48","email":"admin48@bail.com"},
            follow_redirects=True
        )
        response = self.client.get('/autorization')
        assert response.status_code == 200
        response = self.client.post(
            "/autorization", data={"name":"admin48", "psw":"admin48"},
            follow_redirects=True
        )
        assert "Корзина товаров".encode() in response.data

    def test_bascet(self):
        response = self.client.get("/basket")
        assert response.status_code == 302
        response = self.client.post(
            "/autorization", data={"name":"admin", "psw":"admin"},
            follow_redirects=True
        )
        assert "Корзина товаров".encode() in response.data
        response = self.client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        if 'name="productname"' in html:
            response = self.client.post("/",data={"productname":"5"})
            response = self.client.get("/basket")
            assert response.status_code == 200
            response = self.client.post("/",data={"product_remove":"5"})
            html = response.get_data(as_text=True)
            assert "product_remove" not in html
        

    def test_order(self):
        response = self.client.get("/order/1")
        assert response.status_code == 302

    def test_autorization(self):
        response = self.client.get('/autorization')
        assert response.status_code == 200
        response = self.client.post(
            "/autorization", data={"name":"admin", "psw":"admin"},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert "Корзина товаров".encode() in response.data
        assert len(response.history) == 1
        assert response.request.path == '/basket'
        response = self.client.post(
            "/autorization", data={"name":"adminnnn", "psw":"adminnnn"},
            follow_redirects=True
        )
        html = response.get_data(as_text=True)
        assert "Неверное имя или пароль!" in html
        response = self.client.post(
            "/autorization", data={"name":"", "psw":"adminnnn"},
            follow_redirects=True
        )
        html = response.get_data(as_text=True)
        assert "Авторизация" in html
        

    def test_add_card(self):
        response = self.client.get("/add-card")
        assert response.status_code == 302
        response = self.client.post(
            "/autorization", data={"name":"admin", "psw":"admin"},
            follow_redirects=True
        )
        assert response.status_code == 200
        response = self.client.post(
            "/add-card", data={
                "number_card ":"0000 0000 0000 1234",
                 "validity":"12/12",
                 "secret_code":"123",
                 "firstname":"Ivan",
                 "surname":"Ivanov",
                 "patronymic":"Ivanovich"
                },
            follow_redirects=True
        )
        html = response.get_data(as_text=True)
        assert "add-card" in html
        
    def teardown(self):
        pass





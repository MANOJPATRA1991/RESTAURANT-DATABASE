#! /usr/bin/env python3

# VM defaults to Python 2 so, http.server won't work
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

# common gateway interface
#  A CGI script is invoked by an HTTP server, usually to process user input submitted through
#  an HTML <FORM> or <ISINDEX> element.
import cgi

from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem


# 1. Lets our program know that we want to communicate with
# restaurantmenu database
# 2. an Engine, which the Session will use for connection
# resources
engine = create_engine('sqlite:///restaurantmenu.db')

# 1. Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
# 2. Creates connection between our class definitions and
# their corresponding tables in the database
Base.metadata.bind = engine

# 1. Establishes a link of communication between our code execution
# and the engine that we created
# 2. create a configured "DBSession" class
DBSession = sessionmaker(bind=engine)

# 1. A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
# 2. Create a session
session = DBSession()


class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurant"):
                result = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html>" \
                          "<head><link rel='stylesheet'" \
                          " href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'>" \
                          "</head>" \
                          "<body>" \
                          "<h2><a href='/restaurant/new'>Make your own Restaurant</a></h2>" \
                          "<h1>Your go to eat visits:</h1>"
                print(result)
                for data in result:
                    output += "<h3>" + data.name + "</h3>"

                    output += "<button type='submit'>" \
                              "<a href='/restaurant/{}/edit'>Edit</a>".format(data.id) + \
                              "</button> " \
                              "<button type='submit'>" \
                              "<a href='/restaurant/{}/delete'>Delete</a>".format(data.id) + \
                              "</button>"
                output += "</body></html>"

                self.wfile.write(output)
                print(output)
                return

            if self.path.endswith("/restaurant/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body><h1>Create New Restaurant</h1> <a href='/restaurant'>" \
                          "Back to Home</a>"
                output += "<form method='POST' enctype='multipart/form-data' " \
                          "action='/restaurant/new'>" \
                          "<input name='restaurant_name' type='text' placeholder='Enter restaurant name'>" \
                          "<input type='submit' value='Create'></form>"
                output += "</body></html>"

                self.wfile.write(output)
                print(output)
                return

            if self.path.endswith("/edit"):
                restaurant_id = self.path.split("/")[2]
                data = session.query(Restaurant).filter_by(id=restaurant_id).one()

                if data:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body><h1>Rename Restaurant</h1> <a href='/restaurant'>" \
                              "Back to Home</a>"
                    output += "<form method='POST' enctype='multipart/form-data' " \
                              "action='/restaurant/{}/edit'>".format(data.id) + \
                              "<input name='restaurant_name' type='text' placeholder='{}'>"\
                                  .format(data.name) + \
                              "<input type='submit' value='Edit'></form>"
                    output += "</body></html>"

                    self.wfile.write(output)
                    print(output)
                    return

            if self.path.endswith("/delete"):
                restaurant_id = self.path.split("/")[2]
                data = session.query(Restaurant).filter_by(id=restaurant_id).one()

                if data:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body><h1>Are you sure you want to delete?{}</h1>".format(data.name) + \
                              "<a href='/restaurant'>" \
                              "Back to Home</a>"
                    output += "<form method='POST' enctype='multipart/form-data' " \
                              "action='/restaurant/{}/delete'>".format(data.id) + \
                              "<input type='submit' value='Delete'></form>"
                    output += "</body></html>"

                    self.wfile.write(output)
                    print(output)
                    return

        except IOError:
            self.send_error(404, "File Not Found {}".format(self.path))

    def do_POST(self):
        try:
            if self.path.endswith("/restaurant/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    message_content = fields.get('restaurant_name')

                new_restaurant = Restaurant(name=message_content[0])
                session.add(new_restaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurant')
                self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    message_content = fields.get('restaurant_name')
                    restaurant_id = self.path.split("/")[2]

                    data = session.query(Restaurant).filter_by(id=restaurant_id).one()

                    if data:
                        data.name = message_content[0]

                        session.add(data)
                        session.commit()

                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurant')
                        self.end_headers()

            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurant_id = self.path.split("/")[2]

                    data = session.query(Restaurant).filter_by(id=restaurant_id).one()

                    session.delete(data)

                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurant')
                    self.end_headers()

        except:
            pass


def main():

    try:
        port = 8080
        server_address = ('', port)
        httpd = HTTPServer(server_address, WebServerHandler)
        print("Web server is running on port {port}".format(port=port))
        httpd.serve_forever()

    except KeyboardInterrupt:
        print("^C entered, stopping web server...")
        # closes the socket to prevent future operations
        httpd.socket.close()


if __name__ == '__main__':
    main()

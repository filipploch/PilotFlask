from flask_socketio import SocketIO

socketio = SocketIO()


@socketio.on('connect')
def test_connect():
    print('Client connected')


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


# def update_time(value):
#     socketio.emit('update_time', {'time': value})


@socketio.on('toggle_classes')
def toggle_classes(element_id, class_1_name, class_2_name):
    socketio.emit('toggle_classes',
                  {'element_id': element_id,
                   'class_1_name': class_1_name,
                   'class_2_name': class_2_name})


@socketio.on('show_partners')
def show_partners(is_visible):
    socketio.emit('show_partners',
                  {'is_visible': is_visible})
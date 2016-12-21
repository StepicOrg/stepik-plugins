import 'stepic/app';
import CodeEditorView from 'stepic/views/code-editor';

export default Em.Component.extend({
  CodeEditorView:CodeEditorView,
  setInitial: function () {
    var default_source = {
      init_sql: "-- Type your SQL code that initializes a database. Example:\n" +
                "-- \n" +
                "-- CREATE TABLE users (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(20));\n" +
                "-- INSERT INTO users (name) VALUES ('Rainbow Dash');\n" +
                "-- INSERT INTO users (name) VALUES ('Twilight Sparkle');\n",
      solve_sql: "-- Type the solution SQL query. Example:\n" +
                 "-- \n" +
                 "-- INSERT INTO users (name) VALUES ('Fluttershy');\n",
      check_code: "# Type Python 3 code that checks a learner's solution.\n" +
                  "# You can use `cursor` global variable to run checking queries on the database.\n" +
                  "\n" +
                  "def check(query, result):\n" +
                  "    # if \"insert\" not in query.lower():\n" +
                  "    #     return False, \"Use INSERT INTO statement to add a new row\"\n" +
                  "    # count = cursor.execute(\"select * from users where id=3\")\n" +
                  "    # if cursor.fetchone() == (3, \"Fluttershy\"):\n" +
                  "    #     return True\n" +
                  "    # if count == 0:\n" +
                  "    #     return False, \"Cannot find a record with id=3\"\n" +
                  "    # return False, \"Inserted record is incorrect\"\n" +
                  "    return True\n"
    };
    this.set('source', this.get('source') || default_source);
    this.sendAction('sourceUpdated', this.get('source'));
  }.on('init')
});

fs = require('fs');
fs.readFile('{{ SECRET_FILE }}', 'utf8', function (err, data) {
  if (err) {
    console.log(err);
    process.exit(1);
  }
  console.log(data);
});

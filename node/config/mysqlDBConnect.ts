import 'dotenv/config';
const Sequelize = require("sequelize");


const user = process.env.MYSQLDB_USERNAME;
const password = process.env.MYSQLDB_PASSWORD;
const host = process.env.MYSQLDB_HOST;
const port = process.env.MYSQLDB_PORT;
const dbName = process.env.MYSQLDB_NAME;

const sequelize = new Sequelize(
    dbName,
    user,
    password,
    {
        host: host,
        port:port,
        dialect: 'mysql',
        logging:false
    }
);

sequelize.authenticate().then(() => {
    console.log('MYSQL: connection has been established successfully.');
}).catch((error) => {
    console.error('MYSQL: unable to connect to the database: ', error);
});


module.exports = sequelize;
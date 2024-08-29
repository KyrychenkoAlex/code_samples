import mongoose from "mongoose";

import 'dotenv/config';

function mongooseConnectDB() {
    const user = process.env.MONGODB_USERNAME;
    const password = process.env.MONGODB_PASSWORD;
    const host = process.env.MONGODB_HOST;
    const dbName = process.env.MONGODB_NAME;
    const server = process.env.MONGODB_SERVER;

    const connectStr = `${server}://${user}:${password}@${host}/${dbName}?authSource=admin`;

    mongoose
        .connect(connectStr)
        .then(() =>
            console.log('MONGO: connection has been established successfully.')
        )
        .catch((err) => console.log("error connecting to the database", err));
}

module.exports = mongooseConnectDB;
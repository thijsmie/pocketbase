# Examples

In this folder are some examples on how to use the functionality provided by PocketBase with this Python package. The examples all assume there is already a PocketBase instance running locally on port `8123` and an admin account with credentials `email = test@example.com` and `password = test`. You can set these up like so:

```sh
# note: you cannot create an admin before having run the server at least once to init the database
pocketbase serve --http=127.0.0.1:8123 
# ctrl-c
pocketbase admin create test@example.com test
pocketbase serve --http=127.0.0.1:8123
```

If your port, url or credentials are different you can change them in the constants at the top of each example.

## Hello World

A basic overview of the use of the API.

## Working with files

How to upload and download files in PocketBase records.

## Realtime updates

How to subscribe to realtime updates.

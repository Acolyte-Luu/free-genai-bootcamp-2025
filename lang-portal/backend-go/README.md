## Testing

To run the API tests:

```bash
# First time setup
mage setupTestDB

# Terminal 1: Start the server with test database
GO_ENV=test go run cmd/server/main.go

# Terminal 2: Run the tests
cd spec/
bundle exec rspec api/
``` 
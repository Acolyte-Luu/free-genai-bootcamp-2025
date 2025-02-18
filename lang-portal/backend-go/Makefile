.PHONY: test-db-setup test-db-reset test

test-db-setup:
	@echo "Setting up test database..."
	@./scripts/setup_test_db.sh

test-db-reset:
	@echo "Resetting test database..."
	@rm -f config/database/test.db
	@make test-db-setup

test: test-db-reset
	@echo "Running tests..."
	@GO_ENV=test go test ./... 
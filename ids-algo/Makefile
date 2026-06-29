.PHONY: install activate deactivate help

help:
	@echo "Available commands:"
	@echo "  make install    - Create venv and install dependencies"
	@echo "  make activate   - Activate the virtual environment"
	@echo "  make deactivate - Deactivate the virtual environment"

install:
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv venv; \
	fi
	@echo "Installing dependencies..."
	@. venv/bin/activate && pip install -r requirements.txt
	@echo "Done! Run 'make activate' to activate the virtual environment."

activate:
	@echo "To activate the virtual environment, run:"
	@echo "  source venv/bin/activate"
	@echo ""
	@echo "Or use direnv for automatic activation (see README.md)"

deactivate:
	@echo "To deactivate, run:"
	@echo "  deactivate"

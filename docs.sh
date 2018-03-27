#!/bin/sh

pip install epydoc
epydoc --html --name="GlobalPayments.Api" -v -o docs globalpayments

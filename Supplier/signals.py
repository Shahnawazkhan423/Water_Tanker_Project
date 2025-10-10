from django.dispatch import Signal 

order_canceled_by_supplier = Signal()
order_accepted_by_supplier = Signal()
order_on_the_way_by_supplier = Signal()
order_delievery_by_supplier = Signal()
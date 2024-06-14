import functions_framework


@functions_framework.cloud_event
def hello_world(event):
    """Cloud Event Function.
    Args:
        event: Cloud event for the function trigger
    """
    print("Hello, stdout!")
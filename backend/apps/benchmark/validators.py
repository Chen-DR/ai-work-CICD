from infrastructure.ssh.policy import CommandPolicy


def validate_benchmark_params(params: dict) -> list[str]:
    errors = []
    for key, value in params.items():
        if isinstance(value, str):
            if not CommandPolicy.validate_param_value(value):
                errors.append(f"Parameter '{key}' contains dangerous characters")
    return errors

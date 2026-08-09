from tests.evaluation_cases import TASK_1_CASES, TASK_2_CASES


def test_evaluation_case_structure():
    assert len(TASK_1_CASES) >= 5
    assert len(TASK_2_CASES) >= 5

    assert all(case.task == "task1" for case in TASK_1_CASES)
    assert all(case.task == "task2" for case in TASK_2_CASES)

    assert len({case.case_id for case in TASK_1_CASES}) == len(TASK_1_CASES)
    assert len({case.case_id for case in TASK_2_CASES}) == len(TASK_2_CASES)

    assert all(case.input_id for case in TASK_1_CASES)
    assert all(case.input_id for case in TASK_2_CASES)

    assert all(case.acceptance_criteria for case in TASK_1_CASES)
    assert all(case.acceptance_criteria for case in TASK_2_CASES)


def test_adversarial_cases_exist_for_each_task():
    task_1_adversarial = [
        case for case in TASK_1_CASES
        if case.adversarial
    ]

    task_2_adversarial = [
        case for case in TASK_2_CASES
        if case.adversarial
    ]

    assert task_1_adversarial
    assert task_2_adversarial


if __name__ == "__main__":
    test_evaluation_case_structure()
    test_adversarial_cases_exist_for_each_task()

    print("Evaluation case structure tests passed.")
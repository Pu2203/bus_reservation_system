def quicksort(arr, key=lambda x: x):
    if len(arr) <= 1:
        return arr
    pivot = key(arr[len(arr) // 2])
    left = [x for x in arr if key(x) < pivot]
    middle = [x for x in arr if key(x) == pivot]
    right = [x for x in arr if key(x) > pivot]
    return quicksort(left, key) + middle + quicksort(right, key)
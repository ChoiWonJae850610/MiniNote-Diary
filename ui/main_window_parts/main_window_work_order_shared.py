from services.common.field_keys import MaterialTargets

MATERIAL_TARGET_CONFIGS = {
    MaterialTargets.FABRIC: ('fabric_deleted', 'fabric_item_changed', 'fabric_item_added', 'fabric'),
    MaterialTargets.TRIM: ('trim_deleted', 'trim_item_changed', 'trim_item_added', 'trim'),
    MaterialTargets.DYEING: ('dyeing_deleted', 'dyeing_item_changed', 'dyeing_item_added', 'dyeing'),
    MaterialTargets.FINISHING: ('finishing_deleted', 'finishing_item_changed', 'finishing_item_added', 'finishing'),
    MaterialTargets.OTHER: ('other_deleted', 'other_item_changed', 'other_item_added', 'other'),
}

MATERIAL_STACK_NAMES = {target: stack_name for target, (_, _, _, stack_name) in MATERIAL_TARGET_CONFIGS.items()}

def get_field_values(obj):
    class_name = obj.__class__.__name__

    result = "<" + class_name + "("

    f_names = dir(obj)
    for f_name in f_names:
        if f_name == "metadata": continue
        if f_name == "id": continue
        if f_name.startswith("_"): continue
        result += ",{}={}".format(f_name,getattr(obj, f_name))
    result += ")"
    return result

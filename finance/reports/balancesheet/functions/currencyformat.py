def finance_format(list_inp,label_unit):
    try:
        return ["({:0,.2f})".format(abs(round(v,2))) + label_unit if v < 0 else "{0:,.2f}".format((round(v,2))) + label_unit for v in list_inp]
    except:
        return "({:0,.2f})".format(abs(round(list_inp,2))) + label_unit if list_inp < 0 else "{0:,.2f}".format((round(list_inp,2))) + label_unit
from tokenize import tokenize, untokenize, NAME, OP
from io import BytesIO

from transonic.util import TypeHintRemover, format_str
from transonic.analyses import extast


class Backend:
    def __init__(self):
        pass

    def get_code_function(self, fdef):

        transformed = TypeHintRemover().visit(fdef)
        # convert the AST back to source code
        code = extast.unparse(transformed)

        code = format_str(code)

        return code

    def produce_new_code_method(self, fdef, class_def):

        src = self.get_code_function(fdef)

        tokens = []
        attributes = set()

        using_self = False

        g = tokenize(BytesIO(src.encode("utf-8")).readline)
        for toknum, tokval, a, b, c in g:
            # logger.debug((tok_name[toknum], tokval))

            if using_self == "self":
                if toknum == OP and tokval == ".":
                    using_self = tokval
                    continue
                elif toknum == OP and tokval in (",", ")"):
                    tokens.append((NAME, "self"))
                    using_self = False
                else:
                    raise NotImplementedError(
                        f"self{tokval} not supported by Transonic"
                    )

            if using_self == ".":
                if toknum == NAME:
                    using_self = False
                    tokens.append((NAME, "self_" + tokval))
                    attributes.add(tokval)
                    continue
                else:
                    raise NotImplementedError

            if toknum == NAME and tokval == "self":
                using_self = "self"
                continue

            tokens.append((toknum, tokval))

        attributes = sorted(attributes)

        attributes_self = ["self_" + attr for attr in attributes]

        index_self = tokens.index((NAME, "self"))

        tokens_attr = []
        for ind, attr in enumerate(attributes_self):
            tokens_attr.append((NAME, attr))
            tokens_attr.append((OP, ","))

        if tokens[index_self + 1] == (OP, ","):
            del tokens[index_self + 1]

        tokens = tokens[:index_self] + tokens_attr + tokens[index_self + 1 :]

        func_name = fdef.name

        index_func_name = tokens.index((NAME, func_name))
        name_new_func = f"__for_method__{class_def.name}__{func_name}"
        tokens[index_func_name] = (NAME, name_new_func)
        # change recusive calls
        if func_name in attributes:
            attributes.remove(func_name)
            index_rec_calls = [
                index
                for index, (name, value) in enumerate(tokens)
                if value == "self_" + func_name
            ]
            # delete the occurence of "self_" + func_name in function parameter
            del tokens[index_rec_calls[0] + 1]
            del tokens[index_rec_calls[0]]
            # consider the two deletes
            offset = -2
            # adapt all recurrence calls
            for ind in index_rec_calls[1:]:
                # adapt the index to the insertd and deletes
                ind += offset
                tokens[ind] = (tokens[ind][0], name_new_func)
                # put the attributes in parameter
                for attr in reversed(attributes):
                    tokens.insert(ind + 2, (1, ","))
                    tokens.insert(ind + 2, (1, "self_" + attr))
                # consider the inserts
                offset += len(attributes) * 2
        new_code = untokenize(tokens).decode("utf-8")

        return new_code, attributes, name_new_func

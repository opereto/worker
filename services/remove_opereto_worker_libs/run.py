from pyopereto.client import OperetoClient

def remove_opereto_lib():

    try:
        c = OperetoClient()
        c.modify_agent_property(c.input['opereto_agent'], 'opereto.worker', False)
        return c.SUCCESS
    except Exception, e:
        print e
        return 2

if __name__ == "__main__":
    exit(remove_opereto_lib())


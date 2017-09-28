ZabbixApiTools
    Zabbix API调用工具类
    该工具用于调用Zabbix API实现获取主机、主机组、模板、Items信息，创建主机、删除主机、更新主机信息等功能。
    API接口参考：https://www.zabbix.com/documentation/3.2/manual/api/reference
    使用说明：
    1、user_login和get_data为公共函数。
    2、get_host方法需要提供zabbix监控中host_name。返回值为主机组基本信息，并return hostid。
    3、get_grouphost和get_templates方法只能获取所有主机组和模板信息，暂不支持单独获取指定主机组和模板。
    4、get_items方法需要提供参数host_name，根据get_host return的hostid来获取items。
    5、create_host支持的参数为hostip, hostport, groupid, hostname, templateid。其中hostip和hostport为必须提供参数，groupid='12'和templateid='10117'为默认值，hostname如果为空，则hostname=hostip。
    6、del_host方法需要提供参数host_name，根据get_host return的hostid来删除主机。
    7、update_host支持的参数为host_name, template_add_id, groupid, template_clear_id。其中host_name为必须提供参数，更新操作一次只能更新一个参数。
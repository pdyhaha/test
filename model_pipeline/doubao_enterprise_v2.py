from model_pipeline.model.prompt_voc_batch import agent_voc,sample_messages_agent_voc
from model_pipeline.model.prompt_service_action_batch import agent_puke,agent_fuwudongzuo,agent_xueqinggoutong,sample_messages_agent_xueqinggoutong,sample_messages_agent_fuwudongzuo,sample_messages_agent_puke
from model_pipeline.model.prompt_gkyy_v3_batch import agent_price,agent_intention,agent_course_effect,agent_course_consult,sample_messages_agent_price,sample_messages_agent_intention,sample_messages_agent_course_consult,sample_messages_agent_course_effect
from model_pipeline.model.prompt_yyxc import agent_yyxc,sample_messages_agent_yyxc
from model_pipeline.model.prompt_quality_test_batch_v2 import agent_fuwuxiaoji,agent_dihuigongsi,agent_budangxingwei,agent_zhengchaoruma,agent_xujiaxuanchuan
# from model_pipeline.model.prompt_quality_test_batch_v2 import agent_fuwuxiaoji,agent_dihuigongsi,agent_budangxingwei,agent_zhengchaoruma,agent_xujiaxuanchuan,agent_jiaolvyingxiao
from model_pipeline.model.prompt_quality_test_conv_1220 import agent_fwxj_conv,agent_bdxw_conv,agent_zcrm_conv,agent_dhgs_conv,agent_xjxc_conv
# from model_pipeline.model.prompt_quality_test_conv_1220 import agent_fwxj_conv,agent_bdxw_conv,agent_zcrm_conv,agent_dhgs_conv,agent_jlyx_conv,agent_xjxc_conv
# from model_pipeline.model.prompt_quality_detection_v0825 import agent_bdxw,agent_bdxw_conv
# from model_pipeline.model.prompt_quality_detection_v0825 import agent_xujiaxuanchuan,agent_xjxc_conv
from model_pipeline.model.prompt_quality_detection_v0825 import agent_jiaolvyingxiao,agent_jlyx_conv
# from model_pipeline.model.prompt_quality_detection_v0825 import agent_zhengchaoruma,agent_zcrm_conv
# from model_pipeline.model.prompt_quality_detection_v0825 import agent_dihuigongsi,agent_dhgs_conv
# from model_pipeline.model.prompt_quality_detection_v0825 import agent_fuwuxiaoji,agent_fwxj_conv
from model_pipeline.model.prompt_uf_v5 import agent_user_feedback_positive,agent_user_feedback_positive_samples,agent_user_feedback_negative,agent_user_feedback_negative_samples

from volcenginesdkarkruntime import Ark
import time


# 安装时如果使用conda创建的py环境会因为包文件名称过长出现BUG
# 解决方法https://github.com/volcengine/volcengine-python-sdk/issues/5

client = Ark(api_key='e88e554a-454c-4454-bff5-e08e86ff8f96')
# model = 'ep-20240730134105-2gwfm'
# model = 'ep-20240912105919-6x2q9'


# doubao 1.5pro
model = 'ep-20250702102639-vzf49'



def get_result(input,agent_name):
    start_time = time.time()
    input = str(input)

    prompt = ''
    sample_messages = []

    # voc
    if agent_name == 'voc':
        prompt = agent_voc
        sample_messages =sample_messages_agent_voc

    # 服务动作
    elif agent_name == 'xqgt':
        # 学情沟通点评
        prompt = agent_xueqinggoutong
        sample_messages = sample_messages_agent_xueqinggoutong
    elif agent_name == 'puke':
        # 铺课
        prompt = agent_puke
        sample_messages = sample_messages_agent_puke
    elif agent_name == 'fwdz':
        # 其他服务动作
        prompt = agent_fuwudongzuo
        sample_messages = sample_messages_agent_fuwudongzuo


    # 购课异议识别
    # elif agent_name == 'price':
    elif agent_name == 'prc':
        prompt = agent_price
        sample_messages  = sample_messages_agent_price
    # elif agent_name == 'course_effect':
    elif agent_name == 'csef':
        prompt = agent_course_effect
        sample_messages  = sample_messages_agent_course_effect
    # elif agent_name == 'course_consult':
    elif agent_name == 'cscs':
        prompt = agent_course_consult
        sample_messages  = sample_messages_agent_course_consult
    # elif agent_name == 'intention':
    elif agent_name == 'itnt':
        prompt = agent_intention
        sample_messages  = sample_messages_agent_intention

    # 异议消除
    elif agent_name == 'hesitation_dissent':
        prompt = agent_yyxc
        sample_messages  = sample_messages_agent_yyxc



    # 质检
    elif agent_name == 'fwxj':
        # 服务消极
        prompt = agent_fuwuxiaoji
    elif agent_name == 'bdxw':
        # 不当语言/行为
        prompt = agent_budangxingwei
    elif agent_name == 'zcrm':
        # 争吵辱骂
        prompt = agent_zhengchaoruma
    elif agent_name == 'dhgs':
        # 诋毁公司
        prompt = agent_dihuigongsi
    elif agent_name == 'xjxc':
        # 虚假宣传
        prompt = agent_xujiaxuanchuan
    elif agent_name == 'jlyx':
        # 焦虑营销
        prompt = agent_jiaolvyingxiao



    # 质检conv
    elif agent_name == 'fwxj_conv':
        # 服务消极
        prompt = agent_fwxj_conv
    elif agent_name == 'bdxw_conv':
        # 不当语言/行为
        prompt = agent_bdxw_conv
    elif agent_name == 'zcrm_conv':
        # 争吵辱骂
        prompt = agent_zcrm_conv
    elif agent_name == 'dhgs_conv':
        # 诋毁公司
        prompt = agent_dhgs_conv
    elif agent_name == 'xjxc_conv':
        # 虚假宣传
        prompt = agent_xjxc_conv
    elif agent_name == 'jlyx_conv':
        # 焦虑营销
        prompt = agent_jlyx_conv

    # 用户反馈v2

    # elif agent_name == 'user_feedback_positive':
    elif agent_name == 'ufp':
        prompt = agent_user_feedback_positive
        sample_messages = agent_user_feedback_positive_samples

    # elif agent_name == 'user_feedback_negative':
    elif agent_name == 'ufn':
        prompt = agent_user_feedback_negative
        sample_messages = agent_user_feedback_negative_samples



    system_set = [{"role": "system", "content": prompt}]
    input_message = [{"role": "user", "content": input}]
    messages = system_set + sample_messages + input_message

    response = None
    try:

        response = client.chat.completions.create(
            model=model,
            messages=messages,#type:ignore
            temperature=0.6
        )

        reply = response.choices[0].message.content#type:ignore

        input_price = 0.0008
        output_price = 0.002

        input_tokens = response.usage.prompt_tokens#type:ignore
        output_tokens = response.usage.completion_tokens#type:ignore

        cost = input_tokens / 1000 * input_price + output_tokens / 1000 * output_price

        return {
            'input': input,
            'agent_name':agent_name,
            'reply': reply,
            'cost': round(cost,4),
            'succeed_record': 1,
            'execution_time': time.time() - start_time
        }

    except Exception as e:
        if response and response.status_code == 200: #type:ignore
            return {
                'input': input,
                'agent_name':agent_name,
                'reply': '',
                'cost': 0.,
                'succeed_record': 1,
                'execution_time': time.time() - start_time
            }
        else:
            return {
                'input': input,
                'agent_name':agent_name,
                'reply': '',
                'cost': 0.,
                'succeed_record': 0,
                'execution_time': time.time() - start_time
            }



# if __name__ == "__main__":
#     input = """['这是一条引用/回复消息：
# "hello：
# 2.3.4.5"
# ------
# 收到啦，感谢您的反馈哟??！看得出您非常了解和认同绘画对孩子能力的培养。我们叫叫美育会持续助力孩子成长，而且绘画的益处远不止于此，它还能在更多方面帮助孩子全面提升！??
# ']"""
#     result = get_result(input,'xjxc')
#     print(result)
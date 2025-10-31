from model_pipeline.summary.prompt_user_portrait import agent_session_summary_wh_AIS, agent_session_summary_wh_HS
from prompt_user_portrait import agent_session_summary,agent_sum_yy_multi,agent_user_portrait4,agent_session_summary_wh,agent_session_summary_wh_HS,agent_session_summary_wh_AIS
from prompt_user_portrait_2 import agent_user_portrait2
from prompt_user_portrait_3 import agent_user_portrait3
from volcenginesdkarkruntime import Ark
import time


# 安装时如果使用conda创建的py环境会因为包文件名称过长出现BUG
# 解决方法https://github.com/volcengine/volcengine-python-sdk/issues/5

client = Ark(api_key='e88e554a-454c-4454-bff5-e08e86ff8f96')
# model = 'ep-20240730134105-2gwfm'

# doubao pro 32k
# model = 'ep-20240912105919-6x2q9'

# doubao 1.5 pro
model = 'ep-20250702102639-vzf49'
# model = 'ep-20250219100711-fdtfv'




# # deepseek v3
# model = 'ep-20250324175744-v5lzx'


def get_result(input,agent_name):
    start_time = time.time()
    input = str(input)

    prompt = ''
    sample_messages = []

    # jingping
    if agent_name == 'ss':
        prompt = agent_session_summary
    elif agent_name=='yy':
        prompt = agent_sum_yy_multi
    elif agent_name == 'yy2':
        prompt = agent_user_portrait2
    elif agent_name == 'yy3':
        prompt = agent_user_portrait3
    elif agent_name == 'AIS':
        prompt = agent_session_summary_wh_AIS
    elif agent_name == 'HS':
        prompt = agent_session_summary_wh_HS

    system_set = [{"role": "system", "content": prompt}]
    input_message = [{"role": "user", "content": input}]
    messages = system_set + sample_messages + input_message


    response = None
    try:

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )

        reply = response.choices[0].message.content

        input_price = 0.0008
        output_price = 0.002

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

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
        if response and response.status_code == 200:
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

if __name__ == "__main__":
    input = '年课就不报了，他在线下跟着学而思学呢，每周都有课'
    input = '你们这课之前我们五月份报了希望学和学而思了，现在在和他们弄退课的事，还没解决'
    input = '老师，我们在学而思报了，这次就不重复报课了，把目前的课程上完再考虑吧，感谢你对孩子学习的关心'
    input = '又不是学而思、高途，他们是上课要跟进度，而且也可以回看，你看个动画片吵个啥哦'
#     input = '''「ikeou：学而思的是大阅读，写作和阅读一起进行的」
# - - - - - - - - - - - - - - -
# 真人互动'''
    input = '主要你们不像猿辅导学而思机构大又在北京[呲牙]'
    input = '下载什么软件？学而思网校吗？'
    input = '我再权衡一下希望学'
    input = '最近想换学而思，更加适合一年级的教学'
    input = '他数学在学而思上课'
    input = '阅读的话，等把学而思学完了再试试你们的阅读'
    # input = '我们用学而思的摩比系列学过了，都会算，现在在学50以内的加减法了'

    brand = '学而思(希望学)'


    input = '也是斑马的课程，但是斑马没有五年级的数学课程，最高级别是四年级'
    input = '鸡兔同笼，斑马思维都已经学过了'
    brand = '斑马'

    # input = '您好，老师，数学这个挺好的，但是价格太高了，作业帮的299数学学全年，我们计划有时间时体验下那个。'
    # brand  = '作业帮'
    # result = get_result(input,brand,agent_name='jp')
    # print(result['reply'])

    input = '谢谢老师，小朋友要去夏令营，没空学[呲牙]'
    brand = '夏令营'
    result = get_result(input,agent_name='ss')
    print(result['reply'])




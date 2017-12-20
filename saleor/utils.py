from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import RequestContext
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
import cStringIO as StringIO
import cgi
import os
from .site.models import SiteSettings


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), dest=result, link_callback=fetch_resources )
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = "product_chart.pdf"
        response['Content-Disposition'] = 'attachment; filename="product_chart.pdf"'
        content = "inline; filename='%s'" % filename
        response['Content-Disposition'] = content
        return response
    return HttpResponse('Gremlins ate your pdf! %s' % cgi.escape(html))

def fetch_resources(uri, rel):
    path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return path

# Utility function
def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")
    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(source_html, dest=result_file)           # file handle to recieve result
    # close output file
    result_file.close()                 # close output file
    # return True on success and False on errors
    return pisa_status.err

def image64():
    image = 'data:image/png;base64,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'
    return image

def default_logo():
    default = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAWIAAACOCAMAAAA8c/IFAAABCFBMVEX////d3d1OXWT/AADr6+s9T1c7Tlbv8PFJWWDm6OlAUlnMz9Hf39/j4+PP0tTb5eX4+Pl4gocAAABsd33c4uL7Nzf4T09TYWhfbHKlq66NlZlxfIGepai0ubuYn6PhyMiDjJCqsLPe2NjuiYm/w8X2WFjy5dpDWG4wTWDg0NDoqan9ICB/iI1caXD1YGDmsbH6Pz/jwcHslZX8KyvycnIuRE3qoKDnsLDixcX+FBTydnb0aGjsmZn4UFD1X1/5RUUWNEt0dXZjXV6Qf23Cz9yOjZQAACVkTzsAJj8AHDbdz8L/8+yOgHctEQBweISllodab4A+OTd0ZVQeFQ2err1ONA+8yNAsQljQtzWVAAANO0lEQVR4nO2deb+bxhWGQWUTAgkJ2ZIQKJJD3brWje04zp66adOktbuk+/f/JgVmYVY0QiCse+f9wz9flgEeDi9nzowkw9DS0tLS0mqpaOgTuNeKIteyLM24HwG6lYY+lXuoyEV0x+FYE+5WEUk3ME0z1DbRnTi6pibcnQjbDTHdUoEmfLlqumOaribcgRrpQsLu0Cd5s6LoCuACacLtRNIVha4mfIlEKYMm3JGECZkm3JFa0C2lO3VKkqa7mnAHuoBuqVATbtLJdFeJsO5yiNUBXU1YKrXOhCbcTu1SBql0YYJUy4RME1ZSH3QhYd3lIBOyTulWevCEL0x3NeFGdZSQacJCXYVuqQfZbe4w3dWEOanXzjvSgypM9JSQacKl+kp3lQjf+y7HcHQfAuHe092Tus/d5qslZA+S8IdBFxK+l10O91rp7mndU8JGZFmDhm6t+0rYMD4UxNcmPPZXhfxrHDSyxmoMZkBL2foAbtDujl09hsfOqJBzlaOqhvHbx6Xefi5hvPwSbPDyVRvG1y9MjO3rIVYM4+XnvwB6JkY4ew1WfzK7CcJtEedZludZ/qT4d1r8+aT4Q2EvxTCefQcYvhQynH0M70ALwIMUJloiXvz33eJ/7j9/Nv61+LH486fFn1X2UnXjJxDipwLGy1dw5QupVzcSvn6Xox3i90fj6eJXhjE3vv/D4gfj6R8Xv1baTzGMm6wC2cQ3LWximMJEay+uEBvG9+8WPxt/sRQRq4bx7Jcyq5h93d4mBir9XIr498ZfF9Hf3isiVk4qZFZxiU0MVZi4HPHfF//4QRmxahgvfyO2iuXz1jYxWOnncsRPF78zlBErh7HYKpBNfHV+Rjxc6ac14neLPxX/vi9edv/5d/GHUkZhnNHFE1nFJTYxXGGiLeIwq1LhLM9c17Aytby4lGoYi6wC2cRn59vEgKWfa/buKkWWZQZBCBQ04OatAtuELIYD3DDb8pDFtasjNlw3zDfJPI7jebLJG4rzrFWcsImCrlk0fNzG8bZsOSBalnabo2lxKsXm2ZhdMz2AFcHpK4omm33DticQh3la7r1P8/D0odRkJp7vIfmjZCqDzFrF8iu5TRQ8s2Tt1w0XxzjmqGWS8HS1LrQCF7+34S6+s54Q52glvo1WrHL+GshGpnMHHtZ3RgfBBTchDhIP7V3unnYR6uOt441IefZeZhe0Vcw+k9tEkB0LpiNanh9PqiEWqjAxtcvLscv/7shT8Zw53ialztGOuWRvghuJ5tS2vjdht21AHMYMDN9JLyacOiyI4uJGE8lgE2kVyxfwj1c84sB8wzdb3b40ZEs/U7+6lgLO2me2XgGU/IoRy3iCGhlzN9bZKSMWwfBXF9aptvjkq0cDt5uLGZNWETTZhEm3W5+5vQuZbjNGfOehHfC+64rwil9xJ0Fs2XDT0m/QIRNFxLEQhmcruL9ca9iOb4/m+ySZr1AM+BNJaRhaxaNZk01AxMWF2qtt0W5yLF0ZXvDBpTt1CPG23KBw2vl+fufAi/U36CQLX5wfj2u8gnl+EeJRta09Tw+HHX7obWZjCWIMw1kdd+luv8L7XxDHWw8+C5vAAqnVJEF30hQzxlbxSm4TALFnx2le52wZemDsgH7KAeLRxi9PJIPWcIB3pOBQnpE/ygCQKKtX8IhHiVe6CHodujsHHNKZKiCOEYwMrbDgu8EbtSacgvNyNmX/A7IJJ+Cx9OYnrAJ2Or4WdjoC0xntpmT+VyTI+Qi0vKfPAiIu1pGvFhc+pWnREmWnLjw/2mEnuBH/SCwOR9BjqI2FiHcQBpWCjMHBfNZqVBU69S22rBDTAZ5o581WcaLTsQv4b6GBLTPXNkXPjUMlY2AMc7RaFyuojqoL7NanGpmgRpgb6HoCXxEhXkIYJgMJnnLLDBk8GeAhilAYlyRAmMQnsgq5TZQS7RxA291QpzElfZdQit43rO9uqh1s6uFHiLn3YADRkeYkQrwmYJCKqoa9I7tcSaZDnn8dxmZ4ANcgeeNhq5DahFRhRQfkCVjIKNbM+bmOhBpYQd8RhNjh3v478KiTz78A8ZSCQSr3RcatpqNHPm9EGJvhCridJIxnnyDCz8+sr1ljwflCxDYXQDCJs7m+Q/X4eXNyEfJiPtoi4CvkfRIgnnu8ZUNVMHzVohp1aCYWyDCu7rzUKXCfQ24TEsJWVNHxKZoQ8Yo7wx10Cm4FsBBqB4jYZq0UN+MQNQ8eMYQh6m0b1TNN31BFgZOqj0y6MXg4fEneZmKf+PIsxGVhIvG4kACIPf4ZzcAKrnOGnl3+aoRhaNpsGPKIYYvC/Dewyaf9HMEYqReQSQVALDbj2TcY8evTiOtypuUW17TxOJzwHciXEmB3gi/6gD2oNxjY1hMmV9wqHnHCPxe1bDn+ZlWvUNK7iDAOof+IENc2Uejj5tddQXeaH9JdUmq3S9O06uzQJAAwmyteGuBG20tuRcB7qfR2GKiDRZgxj/hOfoOQGXOvitMC95Z8LbvuOAAK12ClMIrJnK3JKspy5n7lk/VM2PGnX0qCmAQyZdWaUIZYZMU4p6gX8IgBDKEVow688O41CqVEjMhKkzClIGyisgppGAfmji9nwoapdweMYilifoUUsfhpzth7yCGWwSCqQS1SCnCajRIhriuYJ6wizD0xXwliwevkfMSC+2Tgd1ntRBzi4DQMcbbRKLMdYhOTRR2Qj4RWEW5wYJTDB1hev4iFlwrX1X1gDjHuw38AiJFNPJoRZU0R4QNsvqC7Pu4OWT6pNN3zvYYOEYszK+hEdb/vuoh9h5Jt1wHnOwmLGNtEGbpP5FYRoE6xn5TlTNfFmDYDIFaOYgYGpTcbUdONggk1k4pErhXW4hMKkiquVXzEbRceYSXJLNsgx/PTXhE3ebHd4MWwdyLMR9rLAl1G5j1JVip4oeIE9AapVcCui7eubhI1Y2LXK2JxseZ0RgEWtMjLGgWqI1y31bXkn8JbfsG84WSzNYMD0Tuk56Qc+43ilnkxKFF453tBs4BZxszSxjBmzVc2sTvc12UkZk4KqOH15sVte3cAxlaCqq32ntC95GHM2ES1SPwZkBBUG8u3JUMY5Pi9IW5dowC1THHO116Z+L5Lw5izidIRxFYB682bkPuwDHjz9IZYUPhUq7RlslLURYIBxTqFPIxFOZrYKhDigPs4Utxv16N1vRi8/Dt3CnLojpAkjAU2US1+DBa/JRejUZMxOw0eDqT1h5gd3S7FV/wFox4QRsdp28Tmjl1JGMYim6is4hlc/i2xHHrxNmI/aAAng/RoFA5XEwUzGU6N3eUgwZJUjFtrLXhqDRzGzNRBWVdu+S1vFSF8lTJzUtC8jT4Rc4OsoeII9J2gzHq54GPrs4yLMC56vRk5H2j2W2lBYvYWrHpcr4J5MXu+GaoM9YiYnVUSwaXU6JQIsQlh7IWoJsKBUwXBqPJWjB+77nS38u0a8bKhrIatov4QOpo0SF9YNfup59edx0Cy0IxDav+m2UDeHefH7mFkO+xCVc2Rg8U5cSHmZm179OiovOJDWMUTvD10ipEf4/PNV+WxVv12oMGcNjzFO9rAiX8OnY2J57TBCX4eBSMyD3E5VbF9yoyme5Zzz/fpZpMmx5Vtg2J6jbjBJsRWgee+evYoOWRZurVBncA89FxpAzMz/f2mOGiMp3Eyg9iSmZkEjDsAY17A8C/tlezrIRUwJ5eYCYwQN9mExCrcvK7I+3iqr5P1XsyEM+GIgwr8VTa/uAFGa6MwymxFMr7mvUGIGwrDMIw/RVYBFxT5cM4Nh3nltMDe68XhJbPkpTD8Ny3QYkU7W/ChDHudIsKNwxtwk5dgk+/AJlVhwhxRQwmevS5T1rQaj6YRO+UiQZiYYIUAMVghLsm79Mc1fEFpaMzvj2E4AhhO3Ga6FdVuVrgWHor3fcfb56aL8uLli+ePSr1uGs9/9rra5vkXS7Mu/WQr/Mmh4izBGyeLS9HzKNblIjafLRSAFTziMVghG/WYxPi4trBAafH7N8Lo5AN60TTbHbfxdr7fZdOyRaKLt1T4bqWA+IImojARZuXH+bbJZtL3xwjpgSU3T8urSQ6tOsQcjJ7UOPzRpGG+Y6Jp7O5DVdPwx4dH+CYRtwzjob4i9yYRtwrjwb7F4yYRtwnj4b4i9zYRnx/GA35F7m0iPj+MB/yOiRtF7Kp+pc3whG8V8ZlhPOiXEN8q4rPCeNhflrlVxOd8h/TAv91zs4jVw3joX5a5WcTKYTw0YWPiVDOihz2JVlIM4+F/WSbcHAp1PbXyKlIK4+EJ37JUvu7xvv6yzLV0Oow14Qt1Mozv62/3XFGnwlgTvlgnwlgT7kCNYawJd6GmMNaEu5E8jB/cjwr3JWkYa8KdSRLGgxcm7pHEYay7zV1KFMaacKcShLEm3LG4MNaFia7FhrEm3L3oMNalnx5Ef2xXE+5DZBhrwr2ICGNNuCfhMNbd5r6EwlgT7k8gjHVhokdVYawJ96oijHW3uV8VYawJ9yxNuHdx3/WjpaWlpaWl9QD1f+VEFoTcqIDNAAAAAElFTkSuQmCC'
    try:
        img = SiteSettings.objects.get(pk=1)
        if img.image:
            return img.image.url
        else:
            raise Exception
    except Exception as e:
        img = default

    return img
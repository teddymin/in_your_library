#wasd: 상하좌우 이동키
#c,x  - > 페이지 넘기기
#v,z -> 책 바꾸기
# g -> 가름끈 설치 및 가름끈 이동
#스페이스 -> 점프
#흰색 버튼 -> 가름끈 제거
#빨간색 버튼 ->  페이지 번호 선택하기

import sys
import os
import subprocess
import pip
pip.main(['install', 'ursina', 'pymupdf','requests','Pillow'])

from PIL import Image
from io import BytesIO
from urllib.parse import quote



import requests
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import pymupdf
import tkinter as tk
from tkinter import simpledialog

# 기본 설정
global garum_num
garum_num = 0
global book_num
book_num = 0
pdf_list = ['writing_1','writing_2','writing_3','writing_4','test'] #파일의 pdf 파일 이름
save_list = [] # 읽기로 한 리스트
pdf_book_list = {} # pdf 클래스 저장용
book_list = {} #엔티티 저장용
shelf_num = 1
w = 0
h = 0
g = 0
floor = 1
global chair_mode
chair_mode = False


pdf_memory = {}
pdf_base_url = 'https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/'

def get_pdf_doc(filename):
    if filename in pdf_memory:
        return pdf_memory[filename]

    url = pdf_base_url + filename
    
    print(f" PDF 다운로드 시도: {filename}")
    print(url)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, verify=False, timeout=5)
        
        if response.status_code == 200:
            pdf_data = BytesIO(response.content)
            doc = pymupdf.open(stream=pdf_data, filetype="pdf")
            pdf_memory[filename] = doc
            print(f" PDF 로딩 성공: {filename}")
            return doc
        else:
            print(f" PDF 없음 (404 Error): {url}")

            
    except Exception as e:
        print(f" PDF 에러: {e}")
        return create_dummy_doc(filename)



texture_memory= {}

def load_web_texture(url):
    if url in texture_memory:
        return texture_memory[url]
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, verify=False, timeout=5)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            tex = Texture(img)
            texture_memory[url] = tex
            print(f"로딩 성공: {url.split('/')[-1]}")
            return tex
        else:
            print(f"다운로드 실패(코드{response.status_code}): {url}")
            return None 
    except Exception as e:
        print(f"에러 발생: {e}")
        return None
    

app = Ursina()

class chair(Entity): #의자 클래스(부모)
    def __init__(self, position = (0,0,0),rotation = (0,0,0),scale = (1,1,1)):
        super().__init__(
            position = position,
            rotation = rotation,
            scale = scale,
        )
        self.chair_1 = Entity(parent = self,model = 'cube',scale = (2,1.5,1.5),position = (0,1,0),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/chair.jpg'))
        self.chair_2 = Entity(parent = self,model = 'cube',scale = (2,2,0.225),position = (0,2.75,8.25+0.1125-9),color = color.gray,collider ='box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/chair.jpg'))
        self.chair_3 = Entity(parent = self,model = 'cube',scale = (0.2,1,1.5-0.225),position = (13.3-0.2-14,2.25,14+0.115-5-9),color = color.gray,collider ='box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/chair.jpg'))
        self.chair_4 = Entity(parent = self,model = 'cube',scale = (0.2,1,1.5-0.225),position = (0.7+0.2,2.25,14+0.115-5-9),color = color.gray,collider ='box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/chair.jpg'))


class pdf_book: #클래스 정의
    def __init__ (self, name, garum,floor, shelf_num, h,g):
        self.name = name
        self.garum = garum
        self.floor = floor
        self.shelf_num = shelf_num
        self.h = h
        self.g = g
        
        

#맵 만들기
main_floor = Entity(model='cube', position = (50,0,50),scale = (100,1,100),color = color.gray,collider='box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/brown_rug.jpg'),texture_scale = (30,20))
main_ceiling = Entity(model = 'cube',position = (12.5,20,12.5),scale = (25,1,60),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall2.jpg'),texture_scale = (1.5, 1))
main_left_wall = Entity(model = 'cube',position = (0,12.5,12.5),scale = (1,25,25),color = color.white,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/window_3.jpg'),texture_scale = (1,1.3))
main_right_wall = Entity(model = 'cube',position = (25,12.5,20),scale = (1,25,40),color = color.white,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall.jpg'),texture_scale = (2.5,2))
main_back_wall = Entity(model = 'cube',position = (12.5,12.5,0),scale = (25,25,1),color = color.white,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall.jpg'),texture_scale = (2.5,2))
main_front_wall = Entity(model = 'cube', position = (7.5,12.5,25),scale = (15,25,1),color = color.white, collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall.jpg'),texture_scale = (2.5,2))
tongro_front_wall = Entity(model = 'cube', position = (20,12.5,40), scale = (10, 25,1),color = color.white, collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall.jpg'),texture_scale=(2.5,2))
tongro_left_wall = Entity(model = 'cube', position = (15,12.5,32.5),scale = (1,25,15),color = color.white,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall.jpg'),texture_scale =(2.5,2))
sf_floor_1 = Entity(model = 'cube', position = (12.5,10,3),scale = (25,1,6),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall2.jpg'),texture_scale = (1.5, 1))
sf_floor_2 = Entity(model = 'cube', position = (22.5,10,19.25),scale = (5,1,26.5),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall2.jpg'),texture_scale = (1.5, 1))
wharo = Entity(model = 'cube', position = (7.5,1.5,34),scale = (5,3,20),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wharo.jpg'))
acja = Entity(model = 'cube', position = (20,4,39.5),scale = (1.5,1.5,0.5),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/ttabong.jpg'))
moon = Entity(model = 'cube' , position = (24,3,37),scale = (1,6,5),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/door.jpg'))
elevator = Entity(model  = 'cube', position = (3,1,9),scale =(6,1,6),color = color.gray , collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall2.jpg'),texture_scale = (1.5, 1))
elevator.dy = 1
acja_down = Entity(model = 'quad',scale = (1,1),parent=acja,y=-0.501, rotation_x=90,color = color.white,double_sided = True,rotation_y = 90,texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall2.jpg'))
acja_up = Entity(model = 'quad',scale = (1,1),parent=acja,y=0.501, rotation_x=90,rotation_y = 90,texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall2.jpg'))
acja_left = Entity(model='quad',scale = (1,1),parent = acja,x=-0.501,texture=load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall2.jpg'),double_sided = True,rotation_y = 270)
acja_right = Entity(model='quad',scale = (1,1),parent = acja,x=+0.501,texture=load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall2.jpg'),double_sided = True,rotation_y = 90)

moon_up = Entity(model = 'quad',scale = (1,1),parent=moon,y=0.501, rotation_x=90,rotation_y = 90,texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall2.jpg'))
moon_left = Entity(model='quad',scale = (1,1),parent = moon,z=-0.501,texture=load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall2.jpg'),double_sided = True,rotation_y = 180)
moon_right = Entity(model='quad',scale = (1,1),parent = moon,z=+0.501,texture=load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_wall2.jpg'),double_sided = True,rotation_y = 0)



garum = Entity(model = 'circle',position = (13.8,30,11.9),scale = (0.3,0.3,0.3),color = color.white,collider = 'mesh',rotation = (0,315,0))
garum_label = Text(text='remove\ngarum',origin=(0, 0),parent=garum,z=-0.01,rotation = (0,0,0),scale = (6,12),color = color.black)

page_select = Entity(model = 'circle', position = (13.8,30,11.9),scale = (0.3,0.3,0.3),color = color.red,collider = 'mesh',rotation = (0,315,0))
page_select_label = Text(text='page\nselect',origin=(0, 0),parent=page_select,z=-0.01,rotation = (0,0,0),scale = (6,12),color = color.black)


book= Entity(model = 'quad', scale = (3.2,1.8), position = (12,30,11),collider = 'box',rotation = (0,315,0),color = color.white)

shelf_01 = Entity(model='cube', scale = (25,0.3,1.5),position = (12.5,2,0.75),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_shelf.jpg'),texture_scale = (3,3))
shelf_02 = Entity(model='cube', scale = (25,0.3,1.5),position = (12.5,4.3,0.75),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_shelf.jpg'),texture_scale = (3,3))
shelf_03 = Entity(model='cube', scale = (25,0.3,1.5),position = (12.5,6.6,0.75),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_shelf.jpg'),texture_scale = (3,3))
shelf_04 = Entity(model='cube', scale = (25,0.3,1.5),position = (12.5,8.9,0.75),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_shelf.jpg'),texture_scale = (3,3))
shelf_21 = Entity(model='cube', scale = (25,0.3,1.5),position = (12.5,12,0.75),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_shelf.jpg'),texture_scale = (3,3))
shelf_22 = Entity(model='cube', scale = (25,0.3,1.5),position = (12.5,14.3,0.75),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_shelf.jpg'),texture_scale = (3,3))
shelf_23 = Entity(model='cube', scale = (25,0.3,1.5),position = (12.5,16.6,0.75),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_shelf.jpg'),texture_scale = (3,3))
shelf_06 = Entity(model='cube', scale = (1.5,0.3,32.5),position = (24.25,2,16.25),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_shelf.jpg'),texture_scale = (3,3))
shelf_07 = Entity(model='cube', scale = (1.5,0.3,32.5),position = (24.25,4.3,16.25),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_shelf.jpg'),texture_scale = (3,3))
shelf_08 = Entity(model='cube', scale = (1.5,0.3,32.5),position = (24.25,6.6,16.25),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_shelf.jpg'),texture_scale = (3,3))
shelf_08 = Entity(model='cube', scale = (1.5,0.3,32.5),position = (24.25,8.9,16.25),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_shelf.jpg'),texture_scale = (3,3))
shelf_24 = Entity(model='cube', scale = (1.5,0.3,32.5),position = (24.25,12,16.25),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_shelf.jpg'),texture_scale = (3,3))
shelf_25 = Entity(model='cube', scale = (1.5,0.3,32.5),position = (24.25,14.3,16.25),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_shelf.jpg'),texture_scale = (3,3))
shelf_26 = Entity(model='cube', scale = (1.5,0.3,32.5),position = (24.25,16.6,16.25),color = color.gray,collider = 'box',texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/wood_shelf.jpg'),texture_scale = (3,3))
main_chair = chair(position = (14,0,9),rotation = (0,315,0)) #chair entity

book.title = pdf_list[0]+'.pdf'
book.pn = 0


for name in pdf_list: #객채 만들기
    pdf_book_list[name] = pdf_book(name,-1,0,0,0,0)
    
    
for i in range(len(pdf_list)):
    if floor == 1:
        if shelf_num == 1:
            pdf_book_list[pdf_list[i]].h = i//43
            pdf_book_list[pdf_list[i]].g = i%43
        if h >= 3 and g>= 42:
            shelf_num = 2
        elif shelf_num == 2:
            pdf_book_list[pdf_list[i]].h = i//63
            pdf_book_list[pdf_list[i]].g = i%63
        pdf_book_list[pdf_list[i]].shelf_num = shelf_num
        if h>= 3 and g>=62 and shelf_num == 2:
            floor = 2
            shelf_num = 1
    else:
        if shelf_num == 1:
            pdf_book_list[pdf_list[i]].h = i//43
            pdf_book_list[pdf_list[i]].g = i%43
        if h >= 3 and g>= 42:
            shelf_num = 2
        elif shelf_num == 2:
            pdf_book_list[pdf_list[i]].h = i//63
            pdf_book_list[pdf_list[i]].g = i%63
        pdf_book_list[pdf_list[i]].shelf_num = shelf_num
    pdf_book_list[pdf_list[i]].floor = floor
        
def open_page(title, page_num):
    global book
    doc = get_pdf_doc(title)
    try:
        page = doc[page_num]
        pix = page.get_pixmap(dpi=150,alpha=False, colorspace=pymupdf.csRGB)
        if pix and pix.width > 0:
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img = img.convert('RGBA')
            book.texture = Texture(img)
            book.pn = page_num
            book.scale_y = 3.2 * pix.height / pix.width
            
    except Exception as e:
        print(f"렌더링 오류: {e}")
        book.texture = None

def garum_action(): # 가름끈 버튼 눌렀을 때
    book.pn = garum_num
    open_page(book.title, book.pn)
    
def move_books(): # pdf_list 에 있는 모든게 객채 정보에 따라 정렬됨
    for i in pdf_list:
        j = pdf_book_list[i]
        if j.shelf_num == 1:
            if j.h<= 3:
                book_list[i].position = (1.5*j.g*0.5,3.15+(j.h+1)*2.3,1.3)
            else:
                book_list[i].position = (1.5+j.g*0.5,10+(j.h+1)*2.3,1.3)
        else:
            if j.h<=3:
                book_list[i].position = (25-1.3,3.15+(j.h+1)*2.3,1.5+j.g*0.5)
            else:
                book_list[i].position = (25-1.3,10+(j.h+1)*2.3,1.5+j.g*0.5)
                




for name in pdf_list:
    g = pdf_book_list[name].g
    h = pdf_book_list[name].h
    shelf_num = pdf_book_list[name].shelf_num
    floor = pdf_book_list[name].floor
    
    if shelf_num == 1:
        book_list[name]= Entity(model = 'cube', scale =(0.5,2,1.5),position = (1.5+g*0.5,3.15+h*2.3+10*(floor-1),1.3),color = color.gray,texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/book.jpg'),name = name,collider = 'box')
    
    else:
        book_list[name]= Entity(model = 'cube', scale =(0.5,2,1.5),position = (23.7,3.15+h*2.3+10*(floor-1),1.5+g*0.5),color = color.gray,texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/book.jpg'),name = name,collider = 'box',rotation_y = 270)
    
    book_down = Entity(model = 'quad',scale = (1,1),parent=book_list[name],y=-0.501, rotation_x=90,color = color.white,double_sided = True,rotation_y = 90,texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/book_under.jpg'))
    book_up = Entity(model = 'quad',scale = (1,1),parent=book_list[name],y=0.501, rotation_x=90,rotation_y = 90,texture = load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/book_under.jpg'))
    book_behind = Entity(model='quad',scale = (1,1),parent = book_list[name],z=-0.501,texture=load_web_texture('https://raw.githubusercontent.com/teddymin/in_your_library/main/assets/book_under.jpg'),double_sided = True,rotation_z = 90)
    book_label = Text(text=name,origin=(0, 0),parent=book_list[name],z=0.51,rotation = (0,180,90),scale = (6,12))



open_page(book.title, book.pn)




def update(): #엘레베이터 함수
    up = True
    if elevator.y <= 0 or elevator.y >= 10:
        elevator.dy *= -1
    elevator.y += elevator.dy*time.dt
    
    
def input(key): #키를 받았을 때
    global chair_mode
    global book_num
    doc = get_pdf_doc(book.title)
    if key == 'g':
        if pdf_book_list[book.title[:-4]].garum != -1:
            book.pn = pdf_book_list[book.title[:-4]].garum
            open_page(book.title,book.pn)
        else:
            pdf_book_list[book.title[:-4]].garum = book.pn
    if key == 'z':
        if book_num >= 1:
            book_num -= 1
            book.title = save_list[book_num]
            book.pn = 0
            open_page(book.title, book.pn)
    if key == 'v':
        if len(save_list)-1 > book_num:
            book_num += 1
            book.title = save_list[book_num]
            book.pn = 0
            open_page(book.title, book.pn)
    if key =='e':
        if chair_mode:
            book.y = 30
            page_select.y = 30
            garum.y = 30
    if key == 'c': #페이지 넘기기
        if book.pn == doc.page_count-1:
            book.pn = -1
        book.pn += 1
        open_page(book.title,book.pn)
    if key == 'x': #페이지 뒤로 넘기기
        book.pn -= 1
        open_page(book.title,book.pn)
    if key =='left mouse down':# 클릭했을 때
        if mouse.hovered_entity == garum: #가름끈 버튼이면
            pdf_book_list[book.title[:-4]].garum = -1
        elif mouse.hovered_entity == page_select: #페이지 선택 버튼이면
            root = tk.Tk()
            root.withdraw()
            val= int(simpledialog.askinteger('페이지 이동', '이동할 페이지 번호를 입력하세요:'))%doc.page_count-1
            if val is not None:
                book.pn = (val-1)%doc.page_count
                open_page(book.title, book.pn)
                
            root.destroy()
            open_page(book.title,book.pn)
        if mouse.hovered_entity:    
            if mouse.hovered_entity.parent == main_chair:
                if not len(save_list) == 0:
                    chair_mode = True
                    print('chair')
                    book.position = (12,4,11)
                    page_select.y = 3.3
                    garum.y= 3.65
                    book.pn = 0
                    book.title = save_list[0]
                    open_page(book.title, book.pn)
                else:
                    print('책을 꺼내십시오')
        if mouse.hovered_entity in book_list.values(): #book list에 있는 것 중 하나라면
            print('book ok')
            move_book = pdf_book_list[mouse.hovered_entity.name]
            if mouse.hovered_entity.name+'.pdf' in save_list:
                book_list[mouse.hovered_entity.name].rotation_z = 0
                book_list[mouse.hovered_entity.name].rotation_y = 0
                if move_book.shelf_num == 1:
                    book_list[mouse.hovered_entity.name].position = (1.5+move_book.g*0.5,3.15+move_book.h*2.3+10*(move_book.floor-1),1.3)
                else:
                    book_list[mouse.hovered_entity.name].position = (23.7,3.15+move_book.h*2.3+10*(move_book.floor-1),1.5+move_book.g*0.5)
                save_list.remove(f'{mouse.hovered_entity.name}.pdf')
                for name in save_list:
                    book_list[name[:-4]].y -= 0.5
            else:
                save_list.append(f'{mouse.hovered_entity.name}.pdf')
                print(save_list)
                book_list[mouse.hovered_entity.name].rotation_z = 90
                book_list[mouse.hovered_entity.name].rotation_y = 180
                book_list[mouse.hovered_entity.name].position = (14,0.5+0.5*(len(save_list)),14)
                
            
            

#EditorCamera()
user = FirstPersonController()
user.position = (10,3,7)
user.gravity = 0.5
user.speed = 5
# from ursina.editor.level_editor import LevelEditor
# editor = LevelEditor()



app.run()
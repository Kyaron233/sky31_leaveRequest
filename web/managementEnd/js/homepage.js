let homepageNav = document.querySelector('#homepage_nav')
let memberMessageNav = document.querySelector('#member_message_nav')
let addMemberNav = document.querySelector('#add_member_nav')
let homePage = document.querySelector('#homepage')
let memberMessagePage = document.querySelector('#member_message')
let addMemberPage = document.querySelector('#add_member')
let navs = document.querySelectorAll('.nav')
let contents = document.querySelectorAll('.content')
function showPage(id) {
  document.querySelector('.active').classList.remove('active')
  document.querySelector(`#${id}_nav`).classList.add('active')
  contents.forEach(content => content.classList.add('hide'))
  document.querySelector(`#${id}`).classList.remove('hide')
}

let allPages = {
  homepage: 'homepage',
  memberMessage: 'member_message',
  addMember: 'add_member'
}

// 初始化页面：根据页面url展示对应页面
showPage(allPages[location.href.split('#')[1]?.split('?')[0] || 'homepage'])
if (location.href.split('#')[1] === 'memberMessage') {
  let items = localStorage.getItem('memberItems')
  if (items) {
    document.querySelector('.message_content').innerHTML = items
  } else {
    location.href = location.href.split('#')[0]
  }
}
// 批量导入
let batchImportBtn = document.querySelector('.batch_import_btn')
let batchImportInput = document.querySelector('input[name="file"]')
batchImportBtn.addEventListener('click', () => {
  // js模拟点击input按钮
  batchImportInput.click()
})
batchImportInput.addEventListener('change', e => {
  // 获取用户选择的文件
  let excelFile = e.target.files[0]
  // 未选择文件时直接退出程序
  if (!excelFile) return
  console.log(excelFile)
  // 判断上传文件类型是否为excel
  let fileType = excelFile.name.split('.').slice(-1)
  // if (fileType != 'xlsx' && fileType != 'xls') {
  //   popupTop.innerHTML = '请上传excel格式的文件！'
  //   popup.classList.remove('hide')
  //   return
  // }
  // 使用FormData携带文件
  const formData = new FormData()
  formData.append('file', excelFile)
  console.log(formData.files)
  formData.forEach((value, key) => {
    console.log(key, value)
  })
  // 将文件上传到服务器
  axios({
    method: 'POST',
    url: '/upload_excel',
    data: formData,
    // data: {
    //   file: excelFile
    // },
    withCredentials: true,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
    .then(result => {
      console.log(result)
    })
    .catch(error => {
      console.dir(error)
    })
})

// 批量删除
let batchDeleteBtn = document.querySelector('.batch_delete_btn')
batchDeleteBtn.addEventListener('click', () => {
  // 点击批量删除按钮弹出提示框：确认删除
  // 对弹窗内容做一些操作
  popupTop.innerHTML = '是否确认全部删除'
  popupBottom.innerHTML = '<button class="determine delete_all">确定</button><button class="cancle close">取消</button>'
  popup.classList.remove('hide')
})

// 事件委托：成员信息
let departmentItems = document.querySelector('.department_items')
departmentItems.addEventListener('click', e => {
  if (e.target.classList.contains('item')) {
    // 获取点击的部门标识
    let departmentId = e.target.id
    // console.log(departmentId)

    // 获取该部门所有成员信息
    axios({
      method: 'GET',
      url: '/query',
      params: { department: departmentId },
      withCredentials: true
    })
      .then(result => {
        console.log(result)
        let memberMessages = result.data.users
        let memberItems = document.querySelector('.member_items')
        // 先清空成员列表
        memberItems.innerHTML = `
          <li class="lhead"><span>正主席 / 团支书</span></li>
          <li class="lhead"><span>分管主席</span></li>
          <li class="lhead"><span>正部</span></li>
          <li class="lhead"><span>副部</span></li>
          <li class="lhead"><span>干事</span></li>
          `
        let lheads = memberItems.querySelectorAll('.lhead')
        // 用以判断各个lhead后有没有lbody，没有的隐藏
        let isDisplays = [0, 0, 0, 0, 0]
        memberMessages.forEach(memberMessage => {
          if (memberMessage.name.length === 2) {
            memberMessage.name = memberMessage.name.split('').join('&nbsp;&nbsp;')
          }
          let li = document.createElement('li')
          li.classList.add('lbody')
          li.innerHTML = `
          <div class="name"><span id="name">${memberMessage.name}</span></div>
          <div class="student_id">学 号|<span id="stu_id">${memberMessage.student_id}</span> </div>
          <div class="tel">电 话|<span id="phone">${memberMessage.tel}</span></div>
          <button class="delete">删除</button>
            `
          let rid = memberMessage.role_in_depart
          if (rid === 4) {
            memberItems.insertBefore(li, lheads[1])
          } else if (rid === 3) {
            memberItems.insertBefore(li, lheads[2])
          } else if (rid === 2) {
            memberItems.insertBefore(li, lheads[3])
          } else if (rid === 1) {
            memberItems.insertBefore(li, lheads[4])
          } else {
            memberItems.appendChild(li)
          }
          let id = Math.abs(rid - 4)
          isDisplays[id] = 1
        })
        for (let i = 0; i < isDisplays.length; i++) {
          isDisplays[i] || lheads[i].classList.add('hide')
        }

        // console.log(memberItems)
        // 将该部门成员信息存入内存，在页面刷新时获取并展示
        localStorage.setItem('memberItems', memberItems.outerHTML)
        // 切换页面到成员信息
        location.href = location.href + '#memberMessage'
      })
      .catch(error => {
        console.dir(error)
      })
    // 跳转到请假申请表列表页面
    // 展示对应部门信息到页面上
    // showPage('member_message')
  }
})

// 添加新成员
let addMemberBtn = document.querySelector('.add_member_btn')
addMemberBtn.addEventListener('click', e => {
  // 跳转到添加新成员页面
  location.href = location.href.split('#')[0] + '#addMember'
})

// 点击首页导航栏返回首页
homepageNav.addEventListener('click', () => {
  location.href = location.href.split('#')[0]
})

let popup = document.querySelector('.popup_shadow')
let popupTop = popup.querySelector('.top')
let popupBottom = popup.querySelector('.bottom')
// 成员信息页面点击删除键时拿到要删除的对象
let deleteEle
// 批量删除页面点击删除键
let deleteAll
popupBottom.addEventListener('click', e => {
  let target = e.target
  // 一个按钮时点击“确定”按钮弹窗消失
  // 两个按钮时点击“取消”按钮弹窗消失
  if (target.classList.contains('close')) {
    popup.classList.add('hide')
    // 取消删除时清空id
    deleteEle && (deleteEle = '')
  } else if (target.classList.contains('delete')) {
    // 点击“确定”按钮删除该成员
    // 隐藏弹窗
    popup.classList.add('hide')
    // 弹窗按钮恢复原样
    popupBottom.innerHTML = '<button class="close">确定</button>'
    deleteMember(deleteEle)
  } else if (target.classList.contains('delete_all')) {
    // 点击“确定”按钮删除所有成员
    // 隐藏弹窗
    popup.classList.add('hide')
    // 弹窗按钮恢复原样
    popupBottom.innerHTML = '<button class="close">确定</button>'
    // 向服务器发送请求执行删除操作
    axios({
      method: 'post',
      url: '/delete/anything',
      withCredentials: true
    })
      .then(result => {
        popupTop.innerHTML = '删除成功!'
        popup.classList.remove('hide')
      })
      .catch(error => {
        console.dir(error)
      })
  }
})

// 监听到页面url发生变化时
window.addEventListener('popstate', () => {
  // 确保展示到正确的页面上
  // 若“#”后为空则返回首页
  pageId = location.href.split('#')[1]?.split('?')[0] || 'homepage'
  showPage(allPages[pageId])
})

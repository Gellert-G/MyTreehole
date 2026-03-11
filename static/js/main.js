document.addEventListener('DOMContentLoaded', function() {
    const likeButtons = document.querySelectorAll('.like-btn');
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    const deleteForms = document.querySelectorAll('.delete-form');
    
    likeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const postId = this.dataset.postId;
            const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
            
            if (!csrfToken) {
                console.error('CSRF token not found');
                return;
            }
            
            fetch(`/post/${postId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                this.querySelector('.like-count').textContent = data.likes_count;
                if (data.liked) {
                    this.classList.add('active');
                } else {
                    this.classList.remove('active');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
    
    favoriteButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const postId = this.dataset.postId;
            const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
            
            if (!csrfToken) {
                console.error('CSRF token not found');
                return;
            }
            
            fetch(`/post/${postId}/favorite`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                this.querySelector('.favorite-count').textContent = data.favorites_count;
                if (data.favorited) {
                    this.classList.add('active');
                } else {
                    this.classList.remove('active');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
    
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            if (confirm('确定要删除这条言论吗？')) {
                this.submit();
            }
        });
    });
    
    const commentForms = document.querySelectorAll('.comment-form');
    commentForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const content = this.querySelector('input[name="content"]').value.trim();
            if (!content) {
                e.preventDefault();
                alert('评论内容不能为空');
            }
        });
    });
});

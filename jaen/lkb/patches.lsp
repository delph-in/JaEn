;;;
;;; simple-minded number conversion; ad-hoc for VerbMobil  (26-oct-99  -  oe)
;;; updated by BMW and FCB

(in-package :mrs)

;;; UTILITY FN

(defun get-rel-feature-value (rel feature)
  ;;; assumes only occurs once
  (when (rel-p rel)
    (dolist (fvpair (rel-flist  rel))
      (when (eql (fvpair-feature fvpair) feature)
        (return (fvpair-value fvpair))))))


(defparameter *nc-times_rel* "times_rel")
(defparameter *nc-plus_rel* "plus_rel")
(defparameter *nc-const_rel* "const_rel")
(defparameter *nc-integer_rel* "card_rel")
(defparameter *nc-term1* (vsym "ARG2"))
(defparameter *nc-term2* (vsym "ARG3"))
(defparameter *nc-factor1* (vsym "ARG2"))
(defparameter *nc-factor2* (vsym "ARG3"))
(defparameter *nc-const_value* (vsym "CARG"))
(defparameter *nc-arg* (vsym "ARG"))

(defun times_rel-p (pred)
  (equal pred *nc-times_rel*))

(defun plus_rel-p (pred)
  (equal pred *nc-plus_rel*))

(defun const_rel-p (pred)
  (or (equal pred *nc-const_rel*) 
      (equal pred *nc-integer_rel*)))

(defun number-convert (mrs)
  (let ((liszt (psoa-liszt mrs))
        constants operators additions deletions)
    (loop
        for relation in liszt
        for pred = (rel-pred relation)
        when (plus_rel-p pred) do (push relation operators)
        when (times_rel-p pred) do (push relation operators)
        when (const_rel-p pred)	do (push relation constants))
    (loop
        for stable = t
        for i from 0
        do
          (loop
              for operator in operators
              for handel = (rel-handel operator)
	      for arg0 = (find 'lkb::arg0  (rel-flist  operator) 
			       :key #'fvpair-feature)
	      for arg1 = (find 'lkb::arg1  (rel-flist  operator) 
			       :key #'fvpair-feature)
              unless (member operator deletions :test #'eq) do
                (let* ((pred (rel-pred operator))
                       (key1 (cond 
                               ((plus_rel-p pred) *nc-term1*)
                               ((times_rel-p pred) *nc-factor1*)))
                       (key2 (cond
                               ((plus_rel-p pred) *nc-term2*)
                               ((times_rel-p pred) *nc-factor2*)))
                       (term1 (get-rel-feature-value operator key1))
                       (const1 (find-const-by-handle 
                                term1 additions constants))
                       (value1 (read-from-string 
				(get-rel-feature-value const1 *nc-const_value*)))
                       (term2 (get-rel-feature-value operator key2))
                       (const2 (find-const-by-handle 
                                term2 additions constants))
                       (value2 (read-from-string 
				(get-rel-feature-value const2 *nc-const_value*)))
                       (value (and value1 value2
                                   (compute-value operator value1 value2))))
                  (when value
                    (push (make-card handel arg0 arg1 value)
			  additions)
                    (push operator deletions)
                    (push const1 deletions)
                    (push const2 deletions)
                    (setf stable nil))))
        until (or stable (>= i 42)))
    (if (or additions deletions)
      (let ((copy (copy-psoa mrs))
            (additions (loop
                           for relation in additions
                           unless (member relation deletions :test #'eq)
                           collect relation))
            (relations (loop
                           for relation in liszt
                           unless (member relation deletions :test #'eq)
                           collect relation)))
        (setf (psoa-liszt copy) (nconc additions relations))
        copy)
      mrs)))

(defun find-const-by-handle (handel new old)
  (or
   (loop
       for relation in new
       thereis (when (and (const_rel-p (rel-pred relation))
                          (eq (rel-handel relation) handel))
                 relation))
   (loop
       for relation in old
       thereis (when (and (const_rel-p (rel-pred relation))
                          (eq (rel-handel relation) handel))
                 relation))))

(defun compute-value (operator term1 term2)
  (let ((pred (rel-pred operator)))
    (cond
     ((plus_rel-p pred) (+ term1 term2))
     ((times_rel-p pred) (* term1 term2)))))

(defun make-card (handel arg0 arg1 value)
  (make-rel
   :pred *nc-integer_rel*
   :handel handel
   :flist (list  
	   arg0
	   arg1
	   (make-fvpair :feature *nc-const_value* 
			:value (format nil "~s" value)))))





